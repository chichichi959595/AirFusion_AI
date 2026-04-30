from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from app.core.geo import Location, haversine_distance_km
from app.domain import AirReading


AIRBOX_STATUS_URL = "https://pm25.lass-net.org/data/last-all-airbox.json"


@dataclass(frozen=True)
class AirBoxProvider:
    url: str = AIRBOX_STATUS_URL
    timeout_seconds: float = 10.0

    async def nearest_reading(self, origin: Location, radius_km: float = 3.0) -> AirReading | None:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.get(self.url)
            response.raise_for_status()
            payload = response.json()

        feeds = payload.get("feeds", []) if isinstance(payload, dict) else []
        candidates = [self._parse_feed(feed, origin) for feed in feeds]
        candidates = [item for item in candidates if item and item.distance_km is not None]
        candidates = [item for item in candidates if item.distance_km <= radius_km]
        return min(candidates, key=lambda item: item.distance_km) if candidates else None

    def _parse_feed(self, feed: dict[str, Any], origin: Location) -> AirReading | None:
        gps_lat = _as_float(_first_present(feed, "gps_lat", "Lat", "lat"))
        gps_lon = _as_float(_first_present(feed, "gps_lon", "Lon", "lon"))
        pm25 = _as_float(_first_present(feed, "s_d0", "PM25", "pm25"))
        if gps_lat is None or gps_lon is None or pm25 is None:
            return None

        label = str(_first_present(feed, "SiteName", "name", "device_id") or "AirBox station")
        location = Location(gps_lat, gps_lon, label=label)
        distance = haversine_distance_km(origin, location)
        return AirReading(
            source=f"AirBox {label}",
            pm25=pm25,
            temperature=_as_float(feed.get("s_t0")),
            humidity=_as_float(feed.get("s_h0")),
            location=location,
            distance_km=round(distance, 3),
            raw=feed,
        )


def _first_present(feed: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = feed.get(key)
        if value not in {None, ""}:
            return value
    return None


def _as_float(value: Any) -> float | None:
    if value in {None, ""}:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
