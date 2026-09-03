# Deadlock — Design Document

## What it is
A single-player roguelike dungeon crawler built in Python. The player
fights through procedurally generated dungeon floors against AI-controlled
enemies. Built in layers, each adding a new system.

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
|   - Auth (players/accounts)  |
|   - Business logic           |
+--------------+---------------+
               | reads/writes
               v
+-----------------------------+
|   Database (PostgreSQL)     |
|   - players table            |
|   - runs table                |
+-----------------------------+
               ^
               | reads (separate HTTP requests)
+--------------+---------------+
|   Web Frontend (React + TS) |
|   - Leaderboard page          |
|   - Player profile page        |
+-----------------------------+
```

Client, API, database, and a web view — three independent programs
talking over HTTP.

## Build phases

| Phase | What gets built | Key concept |
|---|---|---|
| 1. Core loop | Player moves on a grid, walls, one enemy that chases and fights you | Game loop, OOP, grid-based collision |
| 2. Procedural generation | Replace the hand-built map with an algorithm that generates a new dungeon layout every run (BSP) | Recursive algorithm design |
| 3. Enemy AI / pathfinding | Enemies navigate around walls intelligently instead of walking into them | Graph algorithms (A*) |
| 4. Persistence | Save/load runs locally (SQLite) | Basic data persistence |
| 5. Backend API | FastAPI service that accepts run submissions and stores them in PostgreSQL | REST API design, schema design |
| 6. Web frontend | React + TypeScript site showing the live leaderboard | Frontend/backend separation, typed languages |
| 7. Deployment | Docker containers, deployed to a free-tier host | DevOps, environment config |

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

**Phase 3 (done):** Enemy movement replaced with A* pathfinding (find_path), using the standard f = g + h scoring formula and Python's heapq as the priority queue. get_neighbors() restricts expansion to non-wall, in-bounds tiles; heuristic() uses Manhattan distance (fitting for 4-directional grid movement, since diagonal moves aren't allowed). The enemy still attacks directly when orthogonally adjacent (distance 1) and only pathfinds when farther away. Known limitation: the full path is recalculated from scratch on every enemy turn rather than cached — fine at this map size, but a real optimization target if maps grow much larger.

**Phase 4 (done):** Local persistence via SQLite (sqlite3, built into Python's standard library — no server required). init_db() creates a runs table (id, enemies_killed, survived, date) if it doesn't already exist. save_run() inserts a row when the player dies, guarded by a run_saved flag so a run is only recorded once per death, not every frame. get_recent_runs() queries the 5 most recent runs (ORDER BY id DESC LIMIT 5) and displays them on the game-over screen. Pressing R regenerates a fresh dungeon and resets state, allowing multiple runs to be recorded in one play session. This is the same INSERT/SELECT pattern Phase 5's PostgreSQL backend will use, just against a local file instead of a server.

## Status log
- [x] Phase 1 — Core loop
- [x] Phase 2 — Procedural generation
- [X] Phase 3 — Enemy AI / pathfinding
- [X] Phase 4 — Persistence
- [ ] Phase 5 — Backend API
- [ ] Phase 6 — Web frontend
- [ ] Phase 7 — Deployment
