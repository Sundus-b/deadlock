from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from a local .env file, if present

app = FastAPI()

# Connection details for your local PostgreSQL instance.
# The password is read from a .env file (never committed to Git) via
# the DB_PASSWORD variable, instead of being hardcoded here.
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "deadlock",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


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
