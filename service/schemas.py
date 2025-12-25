from typing import Optional, Literal, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator


class AdvertInput(BaseModel):
    lat: float = Field(..., example=54.3245, alias="lat")
    lon: float = Field(..., example=37.3562, alias="lng")
    square: float | float = Field(..., example=200, alias="Общая площадь")
    metro_dist: float | int = Field(..., example=0.25, alias="Расстояние до метро, км")
    floor: int | None = Field(..., example=2, alias="Этаж")
    author_type: Optional[
            Literal["Агентство", "Частное лицо"]
        ] | None = Field(..., example="Частное лицо", alias="Тип автора")
    object_type: Optional[
            Literal["Торговое / Свободного назначения", "Здание", "Офисное помещение"]
        ] = Field(..., example="Офисное помещение", alias="Вид объекта")
    metro_district: str | None = Field(..., example="Лухмановская", alias="Метро/Район")

    model_config = ConfigDict(extra="ignore")

    @field_validator('floor',  mode='after')
    @classmethod
    def validate_floor(cls, value: int | None) -> int:
        if value is None:
            return 1
        return int(value)

    @field_validator('author_type',  mode='after')
    @classmethod
    def validate_author_type(cls, value: str | None) -> int:
        if value is None:
            return "Частное лицо"
        return value


class AdvertOutput(BaseModel):
    pred: float = Field(...)
