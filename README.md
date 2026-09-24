# Deadlock

![gameplay screenshot](Scrnshots/1.png)

A roguelike dungeon crawler built from scratch in Python — procedurally
generated dungeons, grid-based combat, A* enemy pathfinding, and a full
deployed backend + web leaderboard.

## Live deployment
- **API:** https://deadlock-api-bbpx.onrender.com
- **Web leaderboard:** https://deadlock-frontend.onrender.com
- **Download the game (Windows):** https://sundus-b.itch.io/deadlock

Note: the API is hosted on Render's free tier, which spins down after
15 minutes of inactivity. The first request after idling can take
30-60 seconds while it wakes back up — this is expected, not a bug.

## Features
- Grid-based movement and bump-to-attack combat
- Procedurally generated dungeons using recursive Binary Space
  Partitioning (BSP) — a new layout every run, rooms connected by
  automatically carved corridors
- Enemy AI with A* pathfinding — navigates around walls and corners
  instead of getting stuck on them
- Run history persisted to a real PostgreSQL database (hosted on Neon),
  served through a FastAPI backend with validated REST endpoints
  (`POST /runs`, `GET /runs`)
- A React + TypeScript web leaderboard reading live from the API
- Player/enemy HP, a win/lose game-over state, and a quick restart

## Tech stack
Python, Pygame, FastAPI, PostgreSQL (Neon), React, TypeScript

## Running it locally
This project has three parts, each run in its own terminal.

**1. Set up Python dependencies:**
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Create a `.env` file** in the project root with your database
connection string:
```
DATABASE_URL=your_postgres_connection_string_here
```

**3. Start the API** (Terminal 1):
```bash
uvicorn api:app --reload
```

**4. Start the game** (Terminal 2):
```bash
python main.py
```

**5. Start the web leaderboard** (Terminal 3):
```bash
cd frontend
npm install
npm run dev
```
Then open the printed local URL (e.g. http://localhost:5173) in a
browser.

## Controls
- WASD to move
- Walk into an enemy to attack it (bump-to-attack — takes 2 hits to kill)
- Kill the enemy to clear the floor, or die trying — either way, `R`
  starts a new run

## Architecture
See `DESIGN.md` for the full design doc: architecture diagram, build
phases, implementation notes per phase, and deployment details.

## What I learned
- **Recursion**, building the dungeon generator (BSP): splitting a
  rectangle into two, then recursively splitting each of those, until
  pieces are small enough to become rooms. First time implementing a
  recursive algorithm from scratch rather than just using one.
- **Graph search / A***: implementing pathfinding taught me why a
  priority queue matters — always expanding the most promising tile
  (lowest `f = g + h`) instead of just the nearest one is what makes A*
  smarter than a plain breadth-first search.
- **Debugging by isolation**: when the enemy AI silently stopped
  working, tracing it back to a single misplaced `else` block (attached
  to the wrong `if`) taught me to test logic in small, isolated pieces
  rather than assuming a big change is correct just because it runs
  without crashing.
- **Persistence, SQLite to PostgreSQL**: started with SQLite (a local
  file, no server needed) to learn basic INSERT/SELECT persistence,
  then migrated to a real hosted PostgreSQL database (Neon) once the
  project needed a backend other people's requests could reach.
- **REST APIs and schema validation**: building `POST`/`GET` endpoints
  with FastAPI, and using a Pydantic model to automatically validate
  incoming request data before it ever reaches the database.
- **Client-server separation**: splitting the game from the database
  by putting a real API in between, and handling the practical
  realities that come with two separate programs — CORS, a server that
  isn't always running, and keeping secrets (like a database password)
  out of committed code via a `.env` file.
- **Deployment**: getting a Python backend, a database, and a React
  frontend actually live on the internet. Hit a real build failure on
  Render caused by `pygame` needing system graphics libraries the
  server didn't have — fixed by giving the API its own trimmed
  `requirements-api.txt` instead of installing the whole project's
  dependencies. Also hit account-creation issues on both Vercel and
  Netlify (a known bug forcing new accounts into a paid-team flow) and
  worked around it by deploying the frontend on Render instead.
- **Git workflow**: committing incrementally after each working piece
  (not just once at the end) makes the project's history actually show
  how it was built, not just the final result.
