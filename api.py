from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import datetime

app = FastAPI()

DB_FILE = "deadlock.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enemies_killed INTEGER,
            survived BOOLEAN,
            date TEXT
        )
    """)
    conn.commit()
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
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO runs (enemies_killed, survived, date) VALUES (?, ?, ?)",
        (run.enemies_killed, run.survived, timestamp)
    )
    conn.commit()
    conn.close()
    return {"status": "saved"}


@app.get("/runs")
def get_runs(limit: int = 5):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT enemies_killed, survived, date FROM runs ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"enemies_killed": r[0], "survived": bool(r[1]), "date": r[2]} for r in rows]