from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


PlantState = Literal["seedling", "growing", "thirsty", "dead", "bloomed"]


class PlantResponse(BaseModel):
    id: int
    state: PlantState
    created_at: str
    last_watered_at: str | None
    bloom_at: str
    bloom_color: str | None
    days_alive: int
    can_water: bool
    message: str
    thirsty_at: str
    dies_at: str
