from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from random import choice, randint
from typing import Any


FLOWER_COLORS = ["red", "pink", "purple", "blue", "yellow", "orange", "white"]
TERMINAL_STATES = {"dead", "bloomed"}
THIRSTY_AFTER = timedelta(hours=24)
DIES_AFTER = timedelta(hours=48)
SEEDLING_FOR = timedelta(days=2)
MIN_BLOOM_DAYS = 11
MAX_BLOOM_DAYS = 17


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None) -> datetime | None:
    if value is None:
        return None
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def random_bloom_at(now: datetime) -> datetime:
    return now + timedelta(days=randint(MIN_BLOOM_DAYS, MAX_BLOOM_DAYS))


def random_bloom_color() -> str:
    return choice(FLOWER_COLORS)


def new_plant_values(now: datetime | None = None) -> dict[str, Any]:
    created_at = now or utc_now()
    return {
        "state": "seedling",
        "created_at": to_iso(created_at),
        "last_watered_at": None,
        "bloom_at": to_iso(random_bloom_at(created_at)),
        "bloom_color": None,
    }


def care_reference_time(plant: Mapping[str, Any]) -> datetime:
    last_watered_at = parse_time(plant.get("last_watered_at"))
    created_at = parse_time(plant.get("created_at"))
    if created_at is None:
        raise ValueError("Plant is missing created_at")
    return last_watered_at or created_at


def days_alive(plant: Mapping[str, Any], now: datetime | None = None) -> int:
    current_time = now or utc_now()
    created_at = parse_time(plant.get("created_at"))
    if created_at is None:
        return 0
    return max(0, (current_time - created_at).days)


def can_water_plant(plant: Mapping[str, Any], now: datetime | None = None) -> bool:
    if plant.get("state") in TERMINAL_STATES:
        return False

    current_time = now or utc_now()
    last_watered_at = parse_time(plant.get("last_watered_at"))
    if last_watered_at is None:
        return True

    return last_watered_at.date() != current_time.astimezone(timezone.utc).date()


def plant_timeline(plant: Mapping[str, Any]) -> dict[str, str]:
    cared_at = care_reference_time(plant)
    return {
        "thirsty_at": to_iso(cared_at + THIRSTY_AFTER),
        "dies_at": to_iso(cared_at + DIES_AFTER),
    }


def evaluate_plant(
    plant: Mapping[str, Any],
    now: datetime | None = None,
    color_picker: Callable[[], str] = random_bloom_color,
) -> dict[str, Any]:
    if plant.get("state") in TERMINAL_STATES:
        return {}

    current_time = now or utc_now()
    created_at = parse_time(plant.get("created_at"))
    bloom_at = parse_time(plant.get("bloom_at"))

    if created_at is None or bloom_at is None:
        raise ValueError("Plant is missing required timestamps")

    cared_at = care_reference_time(plant)
    time_since_care = current_time - cared_at
    age = current_time - created_at

    next_state = plant.get("state")
    updates: dict[str, Any] = {}

    if time_since_care > DIES_AFTER:
        next_state = "dead"
    elif current_time >= bloom_at:
        next_state = "bloomed"
        if not plant.get("bloom_color"):
            updates["bloom_color"] = color_picker()
    elif time_since_care > THIRSTY_AFTER:
        next_state = "thirsty"
    elif age < SEEDLING_FOR:
        next_state = "seedling"
    else:
        next_state = "growing"

    if next_state != plant.get("state"):
        updates["state"] = next_state

    return updates


def message_for_plant(plant: Mapping[str, Any], now: datetime | None = None) -> str:
    state = plant.get("state")

    if state == "dead":
        return "Your plant dried out. It is time to start again."

    if state == "bloomed":
        color = plant.get("bloom_color") or "bright"
        return f"Your {color} flower bloomed. This plant is complete."

    if state == "thirsty":
        return "Your plant is thirsty and needs water today."

    if state == "seedling":
        return "A tiny sprout is settling into its pot."

    if can_water_plant(plant, now):
        return "Your plant can have today's water whenever you are ready."

    return "Your plant is growing steadily."
