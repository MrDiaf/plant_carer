Ok Overseer

# Plant Carer Agent Notes

Future Codex sessions should start by saying `Ok Overseer` after reading this file, so the user knows project context was loaded.

## Project Overview

Plant Carer is a mobile-first single-plant care game. The user owns one plant, waters it once per day, and tries to keep it alive until it blooms after a randomized two-week-ish period.

## Tech Stack

- Frontend: React + TypeScript + Vite
- Backend: FastAPI + Python
- Database: SQLite
- Runtime/deployment: Docker + Docker Compose

## Docker Commands

```bash
docker compose up --build
docker compose down
docker compose logs -f
docker compose down -v
```

The app is served at `http://localhost:2026`. The backend is reached through the Vite dev proxy inside Docker Compose.

## Important Plant Logic Rules

- Valid states are `seedling`, `growing`, `thirsty`, `dead`, and `bloomed`.
- New plants are created as `seedling` with `last_watered_at = null`, making the first Water action available right away.
- Hydration timing uses `last_watered_at` when present, otherwise `created_at`.
- More than 24 hours without water sets the plant to `thirsty`.
- More than 48 hours without water sets the plant to `dead`.
- Bloom dates are randomized between 11 and 17 days after creation.
- If bloom time arrives while the plant is not dead, the state becomes `bloomed` and a random bloom color is assigned.
- Dead and bloomed plants cannot be watered, but they can be replaced.

## Current Architecture

- `backend/app/plant_logic.py` contains testable lifecycle and time calculations.
- `backend/app/database.py` owns SQLite setup and persistence helpers.
- `backend/app/main.py` defines the REST API:
  - `GET /api/plant`
  - `POST /api/plant/water`
  - `POST /api/plant/replace`
- `frontend/src/api.ts` contains browser API calls.
- `frontend/src/App.tsx` renders the game state and actions.
- `frontend/src/styles.css` contains the mobile-first cozy visual design.

## Known TODOs

- No known TODOs at initial scaffold.
