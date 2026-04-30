from dataclasses import dataclass


@dataclass(frozen=True)
class RiskBand:
    name: str
    min_aqi: int
    max_aqi: int
    color: str
    health_note: str
    action: str


AQI_BANDS = (
    RiskBand("good", 0, 50, "green", "Air quality is good.", "Normal outdoor activity is acceptable."),
    RiskBand(
        "moderate",
        51,
        100,
        "yellow",
        "Air quality is acceptable for most people.",
        "Sensitive groups should watch for respiratory symptoms.",
    ),
    RiskBand(
        "unhealthy_sensitive",
        101,
        150,
        "orange",
        "Air quality is unhealthy for sensitive groups.",
        "Reduce prolonged outdoor exertion and consider a mask.",
    ),
    RiskBand(
        "unhealthy",
        151,
        200,
        "red",
        "Air quality is unhealthy.",
        "Stay indoors, close windows, and run HEPA filtration.",
    ),
    RiskBand(
        "very_unhealthy",
        201,
        300,
        "purple",
        "Air quality is very unhealthy.",
        "Avoid outdoor activity until levels improve.",
    ),
)


def band_for_aqi(aqi: int | None) -> RiskBand:
    if aqi is None:
        return AQI_BANDS[0]
    for band in AQI_BANDS:
        if band.min_aqi <= aqi <= band.max_aqi:
            return band
    return AQI_BANDS[-1]


def estimate_aqi_from_pm25(pm25: float | None) -> int | None:
    if pm25 is None:
        return None
    if pm25 <= 12:
        return round(pm25 / 12 * 50)
    if pm25 <= 35.4:
        return round(51 + (pm25 - 12.1) / (35.4 - 12.1) * 49)
    if pm25 <= 55.4:
        return round(101 + (pm25 - 35.5) / (55.4 - 35.5) * 49)
    if pm25 <= 150.4:
        return round(151 + (pm25 - 55.5) / (150.4 - 55.5) * 49)
    if pm25 <= 250.4:
        return round(201 + (pm25 - 150.5) / (250.4 - 150.5) * 99)
    return 301
