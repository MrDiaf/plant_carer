# Plant Carer

Plant Carer is a small mobile-first web app where you care for one plant at a time. Water it once per day, keep it alive for roughly two weeks, and it will bloom in a random flower color. If it dries out or finishes blooming, you can replace it with a new plant.

## Start

```bash
docker compose up --build
```

Open the app on this computer:

```txt
http://localhost:2026
```

If something else is already using port `2026`, start it on another host port:

```bash
FRONTEND_PORT=2027 docker compose up --build
```

Then open:

```txt
http://localhost:2027
```

## Stop

```bash
docker compose down
```

## Reset the plant and database

```bash
docker compose down -v
```

This removes the SQLite Docker volume and starts fresh on the next `docker compose up --build`.

## Use from another device on the same Wi-Fi

Find your computer's local network IP address, then open:

```txt
http://YOUR_PC_LOCAL_IP:2026
```

For example:

```txt
http://192.168.1.42:2026
```

Keep Docker Compose running on the computer that hosts the app.

## Stack

- Frontend: React, TypeScript, Vite
- Backend: FastAPI, Python
- Database: SQLite stored in a Docker volume
- Runtime: Docker Compose
