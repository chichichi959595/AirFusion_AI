from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.core.geo import Location


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class AirReading:
    source: str
    pm25: float | None = None
    pm10: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    aqi: int | None = None
    location: Location | None = None
    distance_km: float | None = None
    observed_at: datetime = field(default_factory=utc_now)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WeatherReading:
    source: str
    wind_speed: float | None = None
    wind_direction: str | None = None
    rain_probability: float | None = None
    precipitation: float | None = None
    temperature: float | None = None
    humidity: float | None = None
    location: Location | None = None
    distance_km: float | None = None
    observed_at: datetime = field(default_factory=utc_now)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FusionResult:
    location: Location
    local: AirReading
    neighborhood: AirReading | None
    regional: AirReading | None
    weather: WeatherReading | None
    scenario: str
    confidence: float
    risk_aqi: int | None
    risk_band: str
    summary: str
    recommendations: list[str]
    reasoning: list[str]
