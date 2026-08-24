# Deadlock
![gameplay screenshot](screenshots/dungeon.png)

A roguelike dungeon crawler built from scratch in Python — procedurally
generated dungeons, grid-based combat, and simple enemy AI, with more
systems (real pathfinding, persistence, a backend, and a web leaderboard)
planned as the project grows.

## Features
- Grid-based movement and bump-to-attack combat
- Procedurally generated dungeons using recursive Binary Space
  Partitioning (BSP) — a new layout every run
- Rooms connected by corridors, carved automatically
- Simple enemy AI (chases and attacks when adjacent)
- Player/enemy HP, death, and a basic game-over state

## Tech stack
Python, Pygame

(planned: FastAPI + PostgreSQL backend, React + TypeScript web
leaderboard, Docker deployment — see `DESIGN.md`)

## Setup
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install pygame
```

## Run
```bash
python main.py
```

## Controls
- Arrow keys to move
- Walk into an enemy to attack it

## Architecture
See `DESIGN.md` for the full design doc, build phases, and status.

## What I learned
Notes as I go — e.g. first time implementing recursive geometry
splitting (BSP) for procedural generation; debugging how Python's
definition order matters when functions call each other across a file.