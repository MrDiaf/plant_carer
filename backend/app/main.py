from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .database import fetch_current_plant, get_connection, init_db, insert_plant, update_plant
from .models import PlantResponse
from .plant_logic import (
    can_water_plant,
    days_alive,
    evaluate_plant,
    message_for_plant,
    new_plant_values,
    plant_timeline,
    to_iso,
    utc_now,
)


app = FastAPI(title="Plant Carer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


def refresh_plant(connection: Any, plant: dict[str, Any], now: datetime) -> dict[str, Any]:
    updates = evaluate_plant(plant, now)
    if updates:
        return update_plant(connection, plant["id"], updates)
    return plant


def get_or_create_current_plant(connection: Any, now: datetime) -> dict[str, Any]:
    plant = fetch_current_plant(connection)
    if plant is None:
        plant = insert_plant(connection, new_plant_values(now))
    return refresh_plant(connection, plant, now)


def plant_response(
    plant: dict[str, Any],
    now: datetime,
    message: str | None = None,
) -> PlantResponse:
    timeline = plant_timeline(plant)
    return PlantResponse(
        id=plant["id"],
        state=plant["state"],
        created_at=plant["created_at"],
        last_watered_at=plant["last_watered_at"],
        bloom_at=plant["bloom_at"],
        bloom_color=plant["bloom_color"],
        days_alive=days_alive(plant, now),
        can_water=can_water_plant(plant, now),
        message=message or message_for_plant(plant, now),
        thirsty_at=timeline["thirsty_at"],
        dies_at=timeline["dies_at"],
    )


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/plant", response_model=PlantResponse)
def get_plant() -> PlantResponse:
    now = utc_now()
    with get_connection() as connection:
        plant = get_or_create_current_plant(connection, now)
    return plant_response(plant, now)


@app.post("/api/plant/water", response_model=PlantResponse)
def water_plant() -> PlantResponse:
    now = utc_now()
    with get_connection() as connection:
        plant = get_or_create_current_plant(connection, now)

        if plant["state"] == "dead":
            raise HTTPException(
                status_code=409,
                detail="This plant has dried out and cannot be watered.",
            )

        if plant["state"] == "bloomed":
            raise HTTPException(
                status_code=409,
                detail="This plant has already bloomed and is complete.",
            )

        if not can_water_plant(plant, now):
            raise HTTPException(
                status_code=409,
                detail="This plant has already been watered today.",
            )

        watered = update_plant(
            connection,
            plant["id"],
            {"last_watered_at": to_iso(now)},
        )
        plant = refresh_plant(connection, watered, now)

    return plant_response(plant, now, "Your plant drank happily.")


@app.post("/api/plant/replace", response_model=PlantResponse)
def replace_plant() -> PlantResponse:
    now = utc_now()
    with get_connection() as connection:
        plant = get_or_create_current_plant(connection, now)

        if plant["state"] not in {"dead", "bloomed"}:
            raise HTTPException(
                status_code=409,
                detail="This plant is still alive. Keep caring for it.",
            )

        new_plant = insert_plant(connection, new_plant_values(now))

    return plant_response(new_plant, now, "A new plant is ready to grow.")
