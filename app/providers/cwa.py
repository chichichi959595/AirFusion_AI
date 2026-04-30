from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from app.core.geo import Location, haversine_distance_km
from app.domain import WeatherReading


FORECAST_ENDPOINT = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"
OBSERVATION_ENDPOINT = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"


@dataclass(frozen=True)
class CwaProvider:
    api_key: str | None
    forecast_endpoint: str = FORECAST_ENDPOINT
    observation_endpoint: str = OBSERVATION_ENDPOINT
    timeout_seconds: float = 10.0

    async def current_weather_nearest(self, origin: Location) -> WeatherReading | None:
        if not self.api_key:
            return None

        payload = await self._get_json(self.observation_endpoint, params={"format": "JSON"})
        stations = payload.get("records", {}).get("Station", [])
        readings = [self._parse_station(station, origin) for station in stations]
        readings = [reading for reading in readings if reading and reading.distance_km is not None]
        return min(readings, key=lambda reading: reading.distance_km) if readings else None

    async def forecast(self, location_name: str) -> WeatherReading | None:
        if not self.api_key:
            return None

        payload = await self._get_json(
            self.forecast_endpoint,
            params={"format": "JSON", "locationName": location_name},
        )

        locations = payload.get("records", {}).get("location", [])
        if not locations:
            return None

        return self._parse_location(locations[0])

    async def _get_json(self, endpoint: str, *, params: dict[str, str]) -> dict[str, Any]:
        params = {"Authorization": self.api_key or "", **params}
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()

    def _parse_station(self, station: dict[str, Any], origin: Location) -> WeatherReading | None:
        weather = station.get("WeatherElement", {})
        geo = station.get("GeoInfo", {})
        coordinates = geo.get("Coordinates", [])
        location = _station_location(station, coordinates)
        if location is None:
            return None

        distance = haversine_distance_km(origin, location)
        observed_at = _parse_datetime(station.get("ObsTime", {}).get("DateTime"))
        precipitation = _as_float(weather.get("Now", {}).get("Precipitation"))
        wind_direction_degree = _as_float(weather.get("WindDirection"))
        wind_direction = _degree_to_cardinal(wind_direction_degree)

        kwargs = {"observed_at": observed_at} if observed_at else {}
        return WeatherReading(
            source=f"CWA observation {station.get('StationName', 'unknown')}",
            wind_speed=_as_float(weather.get("WindSpeed")),
            wind_direction=wind_direction,
            precipitation=precipitation,
            temperature=_as_float(weather.get("AirTemperature")),
            humidity=_as_float(weather.get("RelativeHumidity")),
            location=location,
            distance_km=round(distance, 3),
            raw=station,
            **kwargs,
        )

    def _parse_location(self, location: dict[str, Any]) -> WeatherReading:
        elements = {
            element.get("elementName"): element.get("time", [{}])[0].get("parameter", {})
            for element in location.get("weatherElement", [])
        }
        return WeatherReading(
            source=f"CWA {location.get('locationName', 'forecast')}",
            rain_probability=_as_float(elements.get("PoP", {}).get("parameterName")),
            humidity=_as_float(elements.get("RH", {}).get("parameterName")),
            raw=location,
        )


def _as_float(value: Any) -> float | None:
    if value in {None, "", "X", "-99", "-98"}:
        return None
    if value == "T":
        return 0.0
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric in {-99, -98}:
        return None
    return numeric


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _station_location(station: dict[str, Any], coordinates: list[dict[str, Any]]) -> Location | None:
    wgs84 = next(
        (
            coordinate
            for coordinate in coordinates
            if str(coordinate.get("CoordinateName", "")).upper() == "WGS84"
        ),
        coordinates[0] if coordinates else None,
    )
    if not wgs84:
        return None

    lat = _as_float(wgs84.get("StationLatitude"))
    lon = _as_float(wgs84.get("StationLongitude"))
    if lat is None or lon is None:
        return None
    return Location(lat=lat, lon=lon, label=str(station.get("StationName") or "CWA station"))


def _degree_to_cardinal(degree: float | None) -> str | None:
    if degree is None:
        return None
    if degree == 990:
        return "Variable"
    directions = (
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    )
    index = round(degree / 22.5) % 16
    return directions[index]
