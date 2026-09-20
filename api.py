from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg2
import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from a local .env file, if present

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deadlock-frontend.onrender.com"],  # temporarily open while setting up Vercel; tighten once the real frontend URL is known
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connection string for the database (Neon in production, or local
# Postgres during development). Read from an environment variable —
# never hardcoded, and never committed to Git.
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id SERIAL PRIMARY KEY,
            enemies_killed INTEGER,
            survived BOOLEAN,
            date TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()


init_db()


class RunSubmission(BaseModel):
    enemies_killed: int
    survived: bool


@app.get("/")
def read_root():
    return {"message": "Deadlock API is running"}


@app.post("/runs")
def create_run(run: RunSubmission):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO runs (enemies_killed, survived, date) VALUES (%s, %s, %s)",
        (run.enemies_killed, run.survived, timestamp)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "saved"}


@app.get("/runs")
def get_runs(limit: int = 5):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT enemies_killed, survived, date FROM runs ORDER BY id DESC LIMIT %s",
        (limit,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"enemies_killed": r[0], "survived": bool(r[1]), "date": r[2]} for r in rows]