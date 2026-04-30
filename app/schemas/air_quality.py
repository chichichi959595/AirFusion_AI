from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.core.geo import Location
from app.domain import AirReading, FusionResult, WeatherReading


SupportedLanguage = Literal["zh-Hant", "en", "ko", "th", "vi"]


class LocationPayload(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lon: float = Field(..., ge=-180, le=180)
    label: str | None = None

    def to_domain(self) -> Location:
        return Location(lat=self.lat, lon=self.lon, label=self.label)


class AirReadingPayload(BaseModel):
    source: str
    pm25: float | None = Field(None, ge=0)
    pm10: float | None = Field(None, ge=0)
    temperature: float | None = None
    humidity: float | None = Field(None, ge=0, le=100)
    aqi: int | None = Field(None, ge=0)
    lat: float | None = Field(None, ge=-90, le=90)
    lon: float | None = Field(None, ge=-180, le=180)
    distance_km: float | None = Field(None, ge=0)
    observed_at: datetime | None = None

    def to_domain(self) -> AirReading:
        location = Location(self.lat, self.lon) if self.lat is not None and self.lon is not None else None
        kwargs = {"observed_at": self.observed_at} if self.observed_at else {}
        return AirReading(
            source=self.source,
            pm25=self.pm25,
            pm10=self.pm10,
            temperature=self.temperature,
            humidity=self.humidity,
            aqi=self.aqi,
            location=location,
            distance_km=self.distance_km,
            **kwargs,
        )


class WeatherPayload(BaseModel):
    source: str
    wind_speed: float | None = Field(None, ge=0)
    wind_direction: str | None = None
    rain_probability: float | None = Field(None, ge=0, le=100)
    precipitation: float | None = Field(None, ge=0)
    temperature: float | None = None
    humidity: float | None = Field(None, ge=0, le=100)
    observed_at: datetime | None = None

    def to_domain(self) -> WeatherReading:
        kwargs = {"observed_at": self.observed_at} if self.observed_at else {}
        return WeatherReading(
            source=self.source,
            wind_speed=self.wind_speed,
            wind_direction=self.wind_direction,
            rain_probability=self.rain_probability,
            precipitation=self.precipitation,
            temperature=self.temperature,
            humidity=self.humidity,
            **kwargs,
        )


class AnalysisRequest(BaseModel):
    location: LocationPayload
    local: AirReadingPayload
    neighborhood: AirReadingPayload | None = None
    regional: AirReadingPayload | None = None
    weather: WeatherPayload | None = None
    language: SupportedLanguage = "zh-Hant"


class AnalysisResponse(BaseModel):
    scenario: str
    confidence: float
    risk_aqi: int | None
    risk_band: str
    summary: str
    recommendations: list[str]
    reasoning: list[str]
    llm_prompt: str
    message: str | None = None
    message_source: str | None = None

    @classmethod
    def from_domain(
        cls,
        result: FusionResult,
        *,
        prompt: str,
        message: str | None = None,
        message_source: str | None = None,
    ) -> "AnalysisResponse":
        return cls(
            scenario=result.scenario,
            confidence=result.confidence,
            risk_aqi=result.risk_aqi,
            risk_band=result.risk_band,
            summary=result.summary,
            recommendations=result.recommendations,
            reasoning=result.reasoning,
            llm_prompt=prompt,
            message=message,
            message_source=message_source,
        )


class SensorReportRequest(BaseModel):
    device_id: str = "arduino-sensor01"
    language: SupportedLanguage = "zh-Hant"
    lat: float = Field(24.996222, ge=-90, le=90)
    lon: float = Field(121.576211, ge=-180, le=180)
    location_label: str = "Taipei Wenshan"
    pm25: float = Field(..., ge=0)
    pm10: float | None = Field(None, ge=0)
    temperature: float | None = None
    humidity: float | None = Field(None, ge=0, le=100)
    neighborhood_pm25: float | None = Field(
        None,
        ge=0,
        description="Optional AirBox value for local testing. Live AirBox can be connected later.",
    )
    regional_pm25: float | None = Field(None, ge=0)
    regional_aqi: int | None = Field(None, ge=0)
    wind_speed: float | None = Field(None, ge=0)
    wind_direction: str | None = None
    rain_probability: float | None = Field(None, ge=0, le=100)


class SensorReportResponse(BaseModel):
    ok: bool
    message: str
    message_source: str
    language: SupportedLanguage
    neighborhood_source: str | None = None
    neighborhood_station: str | None = None
    neighborhood_distance_km: float | None = None
    neighborhood_pm25: float | None = None
    neighborhood_temperature: float | None = None
    neighborhood_humidity: float | None = None
    regional_source: str | None = None
    regional_station: str | None = None
    regional_distance_km: float | None = None
    regional_pm25: float | None = None
    regional_aqi: int | None = None
    weather_source: str | None = None
    weather_station: str | None = None
    weather_distance_km: float | None = None
    wind_speed: float | None = None
    wind_direction: str | None = None
    humidity: float | None = None
    precipitation: float | None = None
    scenario: str
    confidence: float
    summary: str
    recommendations: list[str]
    llm_prompt: str
