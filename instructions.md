# Plant Care Web App Instructions

Build and run the app with Docker Compose:

```bash
docker compose up --build
```

The frontend is available at:

```txt
http://localhost:2026
```

The app lets the user care for one plant at a time. The plant can be `seedling`, `growing`, `thirsty`, `dead`, or `bloomed`.

Core rules:

- The user can water a living plant once per UTC day.
- If more than 24 hours pass since the last watering, or since creation for a never-watered plant, the plant becomes `thirsty`.
- If more than 48 hours pass since that same care time, the plant becomes `dead`.
- A dead or bloomed plant cannot be watered.
- Each new plant gets a randomized bloom time between 11 and 17 days after creation.
- If the bloom time arrives while the plant is still alive, it becomes `bloomed` and receives a random flower color.
- A dead or bloomed plant can be replaced with a new plant.
