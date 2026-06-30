from __future__ import annotations

import os
import sqlite3
from collections.abc import Mapping
from typing import Any


DATABASE_PATH = os.getenv("DATABASE_PATH", "/data/plant-carer.sqlite3")


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    path = os.getenv("DATABASE_PATH", DATABASE_PATH)
    _ensure_parent_dir(path)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_watered_at TEXT,
                bloom_at TEXT NOT NULL,
                bloom_color TEXT
            )
            """
        )
        connection.commit()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


def fetch_current_plant(connection: sqlite3.Connection) -> dict[str, Any] | None:
    row = connection.execute(
        "SELECT * FROM plants ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row_to_dict(row)


def insert_plant(
    connection: sqlite3.Connection, values: Mapping[str, Any]
) -> dict[str, Any]:
    cursor = connection.execute(
        """
        INSERT INTO plants (state, created_at, last_watered_at, bloom_at, bloom_color)
        VALUES (:state, :created_at, :last_watered_at, :bloom_at, :bloom_color)
        """,
        dict(values),
    )
    connection.commit()
    row = connection.execute(
        "SELECT * FROM plants WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    plant = row_to_dict(row)
    if plant is None:
        raise RuntimeError("Failed to load newly created plant")
    return plant


def update_plant(
    connection: sqlite3.Connection, plant_id: int, values: Mapping[str, Any]
) -> dict[str, Any]:
    if not values:
        plant = connection.execute(
            "SELECT * FROM plants WHERE id = ?", (plant_id,)
        ).fetchone()
        loaded = row_to_dict(plant)
        if loaded is None:
            raise RuntimeError("Plant not found")
        return loaded

    assignments = ", ".join(f"{key} = :{key}" for key in values)
    params = dict(values)
    params["id"] = plant_id
    connection.execute(f"UPDATE plants SET {assignments} WHERE id = :id", params)
    connection.commit()
    row = connection.execute("SELECT * FROM plants WHERE id = ?", (plant_id,)).fetchone()
    plant = row_to_dict(row)
    if plant is None:
        raise RuntimeError("Plant not found after update")
    return plant
