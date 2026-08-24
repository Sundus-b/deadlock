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

## Status log
- [x] Phase 1 — Core loop
- [x] Phase 2 — Procedural generation
- [ ] Phase 3 — Enemy AI / pathfinding
- [ ] Phase 4 — Persistence
- [ ] Phase 5 — Backend API
- [ ] Phase 6 — Web frontend
- [ ] Phase 7 — Deployment
