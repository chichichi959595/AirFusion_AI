from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.geo import Location, haversine_distance_km
from app.domain import AirReading


AQI_ENDPOINT = "https://data.moenv.gov.tw/api/v2/AQX_P_432"


@dataclass(frozen=True)
class MoenvProvider:
    api_key: str | None
    endpoint: str = AQI_ENDPOINT
    timeout_seconds: float = 10.0

    async def nearest_reading(self, origin: Location) -> AirReading | None:
        payload = await self._get_json()
        records = _records_from_payload(payload)
        readings = [self._parse_record(record, origin=origin) for record in records]
        readings = [reading for reading in readings if reading and reading.distance_km is not None]
        return min(readings, key=lambda reading: reading.distance_km) if readings else None

    async def site_reading(self, site_name: str) -> AirReading | None:
        payload = await self._get_json()
        records = _records_from_payload(payload)
        for record in records:
            if str(record.get("sitename", "")).lower() == site_name.lower():
                return self._parse_record(record)
        return None

    async def _get_json(self) -> dict[str, Any]:
        params = {"format": "json"}
        if self.api_key:
            params["api_key"] = self.api_key
        params["limit"] = "1000"

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(self.endpoint, params=params)
            response.raise_for_status()
            return response.json()

    def _parse_record(
        self,
        record: dict[str, Any],
        *,
        origin: Location | None = None,
    ) -> AirReading | None:
        lat = _as_float(record.get("latitude"))
        lon = _as_float(record.get("longitude"))
        location = (
            Location(lat, lon, label=str(record.get("sitename") or "MOENV station"))
            if lat is not None and lon is not None
            else None
        )
        distance = haversine_distance_km(origin, location) if origin and location else None
        return AirReading(
            source=f"MOENV {record.get('sitename', 'unknown')}",
            pm25=_as_float(record.get("pm2.5") or record.get("pm25")),
            pm10=_as_float(record.get("pm10")),
            aqi=_as_int(record.get("aqi")),
            location=location,
            distance_km=round(distance, 3) if distance is not None else None,
            raw=record,
        )


def _records_from_payload(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [record for record in payload if isinstance(record, dict)]
    if isinstance(payload, dict):
        records = payload.get("records", [])
        return records if isinstance(records, list) else []
    return []


def _as_float(value: Any) -> float | None:
    if value in {None, "", "-"}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_int(value: Any) -> int | None:
    numeric = _as_float(value)
    return int(numeric) if numeric is not None else None
