from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Iterable, Protocol, TypeVar


EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True)
class Location:
    lat: float
    lon: float
    label: str | None = None


class HasLocation(Protocol):
    location: Location


T = TypeVar("T", bound=HasLocation)


def haversine_distance_km(a: Location, b: Location) -> float:
    lat1 = radians(a.lat)
    lon1 = radians(a.lon)
    lat2 = radians(b.lat)
    lon2 = radians(b.lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(h))


def nearest_station(origin: Location, stations: Iterable[T], radius_km: float | None = None) -> T | None:
    nearest: tuple[float, T] | None = None

    for station in stations:
        distance = haversine_distance_km(origin, station.location)
        if radius_km is not None and distance > radius_km:
            continue
        if nearest is None or distance < nearest[0]:
            nearest = (distance, station)

    return nearest[1] if nearest else None
