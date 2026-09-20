# Deadlock — Design Document

## What it is
A single-player roguelike dungeon crawler built in Python. The player
fights through procedurally generated dungeon floors against AI-controlled
enemies. Built in layers, each adding a new system.

## Live deployment
- API: https://deadlock-api-bbpx.onrender.com
- Web leaderboard: https://deadlock-frontend.onrender.com

Note: the API is hosted on Render's free tier, which spins down after
15 minutes of inactivity. The first request after idling can take
30-60 seconds while it wakes back up — expected, not a bug.

## Architecture

```
+-----------------------------+
|   Game Client (Pygame)      |   <- played directly
|   Python                    |
|                              |
|   - Rendering                |
|   - Input handling           |
|   - Game loop                |
|   - Entities (Player/Enemy)  |
|   - Dungeon generation       |
|   - Pathfinding (AI)         |
+--------------+---------------+
               | sends run data (score, time, floor)
               | HTTP requests
               v
+-----------------------------+
|   Backend API (FastAPI)     |
|   Python                    |
|                              |
|   - Receives/validates runs  |
|   - Business logic           |
+--------------+---------------+
               | reads/writes
               v
+-----------------------------+
|   Database (PostgreSQL)     |
|   - runs table                |
+-----------------------------+
               ^
               | reads (separate HTTP requests)
+--------------+---------------+
|   Web Frontend (React + TS) |
|   - Leaderboard page          |
+-----------------------------+
```

Client, API, database, and a web view — four independent programs,
now all deployed and talking to each other over the public internet.

## Build phases

| Phase | What gets built | Key concept |
|---|---|---|
| 1. Core loop | Player moves on a grid, walls, one enemy that chases and fights you | Game loop, OOP, grid-based collision |
| 2. Procedural generation | Replace the hand-built map with an algorithm that generates a new dungeon layout every run (BSP) | Recursive algorithm design |
| 3. Enemy AI / pathfinding | Enemies navigate around walls intelligently instead of walking into them | Graph algorithms (A*) |
| 4. Persistence | Save/load runs (SQLite, later PostgreSQL) | Basic data persistence |
| 5. Backend API | FastAPI service that accepts run submissions and stores them in PostgreSQL | REST API design, schema design |
| 6. Web frontend | React + TypeScript site showing the live leaderboard | Frontend/backend separation, typed languages |
| 7. Deployment | Real hosting for the API, database, and frontend | DevOps, environment config, CORS, secrets management |

## Current implementation notes

**Phase 1 (done):** player/enemy state tracked via variables and
functions; bump-to-attack combat; Manhattan-distance based chase AI;
grid collision via `is_wall()`.

**Phase 2 (done):** Dungeon generated with recursive Binary Space
Partitioning (`split_recursive`) — splits the map into a binary tree of
rectangles, shrinks each into a room (`rect_to_room`), carves rooms and
L-shaped corridors into a grid (`rooms_to_map`, `carve_corridor`).
Player and enemy spawn at `room_center()` of the first and last
generated rooms.

**Phase 3 (done):** Enemy movement replaced with A* pathfinding
(`find_path`), using the standard `f = g + h` scoring formula and
Python's `heapq` as the priority queue. `get_neighbors()` restricts
expansion to non-wall, in-bounds tiles; `heuristic()` uses Manhattan
distance (fitting for 4-directional grid movement, since diagonal
moves aren't allowed). The enemy still attacks directly when
orthogonally adjacent (distance 1) and only pathfinds when farther
away. Known limitation: the full path is recalculated from scratch on
every enemy turn rather than cached — fine at this map size, but a
real optimization target if maps grow much larger.

**Phase 4 (done):** Local persistence via SQLite (`sqlite3`, built
into Python's standard library). `init_db()` creates a `runs` table
(`id`, `enemies_killed`, `survived`, `date`) if it doesn't already
exist. `save_run()` inserts a row when the player dies, guarded by a
`run_saved` flag so a run is only recorded once per death, not every
frame. `get_recent_runs()` queries the 5 most recent runs
(`ORDER BY id DESC LIMIT 5`) and displays them on the game-over
screen. Pressing `R` regenerates a fresh dungeon and resets state.
Also added a live HP display, a win condition (killing the enemy ends
the run as a "win," not just dying), a turn-by-turn message log, and
switched player controls from arrow keys to WASD (the enemy is
AI-only, never player-controlled). Fixed a bug where the enemy's turn
was triggered by *any* keypress instead of only real WASD moves.

**Phase 5 (done):** Built a FastAPI backend (`api.py`) exposing
`POST /runs` (accepts a run via a Pydantic `RunSubmission` model —
FastAPI validates the request body automatically against that schema)
and `GET /runs` (returns the most recent runs as JSON, ordered newest
first). The client (`main.py`) no longer touches a database directly —
`save_run()` and `get_recent_runs()` now make HTTP calls via the
`requests` library, with a `try/except` around each in case the API
isn't running. The game and API run as two separate processes, in two
terminals.

Switched the database from SQLite to real PostgreSQL, connected via
`psycopg2`. Differences from SQLite worth remembering: PostgreSQL uses
`%s` placeholders instead of `?`, and `SERIAL PRIMARY KEY` instead of
`AUTOINCREMENT`.

**Security note:** the database password/connection string is never
hardcoded in `api.py` or committed to Git. It's stored in a local
`.env` file (loaded via `python-dotenv`, `os.getenv(...)`), and `.env`
is listed in `.gitignore` so it never reaches GitHub. Hardcoding a real
password directly in committed code is a common beginner mistake that
exposes it to anyone who views the repository.

Also fixed a performance issue: the game-over screen was originally
calling `GET /runs` on every single rendered frame (~60 times per
second) instead of once. Fixed by fetching once into a
`cached_recent_runs` variable right when the run is saved, and reusing
that cached list for drawing.

**Phase 6 (done):** Built a React + TypeScript frontend (`frontend/`,
scaffolded with Vite) showing a leaderboard. `App.tsx` uses `useState`
to hold fetched runs and `useEffect` to fetch them once on load,
calling the API's `GET /runs` endpoint via the browser's built-in
`fetch()`. An `interface Run` defines the expected shape of each run,
mirroring the Pydantic model on the backend. Required enabling CORS on
the API (`CORSMiddleware`) so the browser would allow requests from
the frontend's different port.

**Phase 7 (done):** Deployed all three remaining pieces:
- **Database:** migrated from local PostgreSQL to Neon (managed,
  serverless Postgres, permanent free tier). Connection now goes
  through a single `DATABASE_URL` env var instead of separate
  host/port/user/password fields.
- **API:** deployed to Render as a Web Service. Had to split
  `requirements.txt` into a separate `requirements-api.txt` — the
  original file included `pygame`, which the API doesn't need and
  which failed to build on Render's server (no SDL/graphics libraries
  available there). Deploying only what a service actually needs,
  rather than the whole project's dependencies, was the real fix.
- **Frontend:** attempted Vercel and Netlify first; both blocked new
  account creation behind a forced "create a paid team" flow (a known
  issue reported by other users, not specific to this project).
  Deployed as a Render Static Site instead, since that account already
  had a working, unblocked setup.
- **CORS:** temporarily opened to all origins (`allow_origins=["*"]`)
  to unblock testing while the frontend's exact deployed URL was still
  unknown; worth tightening to the specific frontend URL as a future
  polish step.

## Status log
- [x] Phase 1 — Core loop
- [x] Phase 2 — Procedural generation
- [x] Phase 3 — Enemy AI / pathfinding
- [x] Phase 4 — Persistence
- [x] Phase 5 — Backend API
- [x] Phase 6 — Web frontend
- [x] Phase 7 — Deployment

**All 7 phases complete.**
