from typing import Optional, Literal, Dict, List
from pydantic import BaseModel, Field, ConfigDict


class YandexBaseInput(BaseModel):
    lat: float = Field(..., example=55.625578)
    lon: float = Field(..., example=37.606392)
    radius: int = Field(..., example=600)
    rubrics: List[List[str]] = Field(..., example=[["Кафе"]])


class YandexBaseOutput(BaseModel):
    data: Dict[str, int] | None