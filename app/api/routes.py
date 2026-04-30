from fastapi import APIRouter

from app.core.config import get_settings
from app.core.geo import Location
from app.domain import AirReading, WeatherReading
from app.providers.airbox import AirBoxProvider
from app.providers.cwa import CwaProvider
from app.providers.moenv import MoenvProvider
from app.schemas.air_quality import (
    AnalysisRequest,
    AnalysisResponse,
    SensorReportRequest,
    SensorReportResponse,
)
from app.services.advisor import AdvisorService
from app.services.fusion import FusionService
from app.services.prompting import build_air_quality_prompt


router = APIRouter()
fusion_service = FusionService()
advisor_service = AdvisorService()
settings = get_settings()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "airfusion-ai"}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_air_quality(payload: AnalysisRequest) -> AnalysisResponse:
    result = fusion_service.analyze(
        location=payload.location.to_domain(),
        local=payload.local.to_domain(),
        neighborhood=payload.neighborhood.to_domain() if payload.neighborhood else None,
        regional=payload.regional.to_domain() if payload.regional else None,
        weather=payload.weather.to_domain() if payload.weather else None,
    )
    prompt = build_air_quality_prompt(result, language=payload.language)
    message, source = await advisor_service.create_user_message(result, prompt, language=payload.language)
    return AnalysisResponse.from_domain(result, prompt=prompt, message=message, message_source=source)


@router.post("/sensor/report", response_model=SensorReportResponse)
async def create_sensor_report(payload: SensorReportRequest) -> SensorReportResponse:
    location = Location(payload.lat, payload.lon, payload.location_label)
    local = AirReading(
        source=payload.device_id,
        pm25=payload.pm25,
        pm10=payload.pm10,
        temperature=payload.temperature,
        humidity=payload.humidity,
    )
    neighborhood = await _load_neighborhood_air_quality(location, payload)
    regional = await _load_regional_air_quality(location, payload)
    weather = await _load_weather(location, payload)

    result = fusion_service.analyze(
        location=location,
        local=local,
        neighborhood=neighborhood,
        regional=regional,
        weather=weather,
    )
    prompt = build_air_quality_prompt(result, language=payload.language)
    message, source = await advisor_service.create_user_message(result, prompt, language=payload.language)
    return SensorReportResponse(
        ok=True,
        message=message,
        message_source=source,
        language=payload.language,
        neighborhood_source=neighborhood.source if neighborhood else None,
        neighborhood_station=neighborhood.location.label if neighborhood and neighborhood.location else None,
        neighborhood_distance_km=neighborhood.distance_km if neighborhood else None,
        neighborhood_pm25=neighborhood.pm25 if neighborhood else None,
        neighborhood_temperature=neighborhood.temperature if neighborhood else None,
        neighborhood_humidity=neighborhood.humidity if neighborhood else None,
        regional_source=regional.source if regional else None,
        regional_station=regional.location.label if regional and regional.location else None,
        regional_distance_km=regional.distance_km if regional else None,
        regional_pm25=regional.pm25 if regional else None,
        regional_aqi=regional.aqi if regional else None,
        weather_source=weather.source if weather else None,
        weather_station=weather.location.label if weather and weather.location else None,
        weather_distance_km=weather.distance_km if weather else None,
        wind_speed=weather.wind_speed if weather else None,
        wind_direction=weather.wind_direction if weather else None,
        humidity=weather.humidity if weather else None,
        precipitation=weather.precipitation if weather else None,
        scenario=result.scenario,
        confidence=result.confidence,
        summary=result.summary,
        recommendations=result.recommendations,
        llm_prompt=prompt,
    )


async def _load_neighborhood_air_quality(
    location: Location,
    payload: SensorReportRequest,
) -> AirReading | None:
    try:
        live_neighborhood = await AirBoxProvider().nearest_reading(location, radius_km=10)
        if live_neighborhood:
            return live_neighborhood
    except Exception:
        pass

    if payload.neighborhood_pm25 is not None:
        return AirReading(source="manual-airbox-fallback", pm25=payload.neighborhood_pm25)
    return None


async def _load_regional_air_quality(
    location: Location,
    payload: SensorReportRequest,
) -> AirReading | None:
    try:
        live_regional = await MoenvProvider(settings.moenv_api_key).nearest_reading(location)
        if live_regional:
            return live_regional
    except Exception:
        pass

    if payload.regional_pm25 is not None or payload.regional_aqi is not None:
        return AirReading(
            source="manual-moenv-fallback",
            pm25=payload.regional_pm25,
            aqi=payload.regional_aqi,
        )
    return None


async def _load_weather(
    location: Location,
    payload: SensorReportRequest,
) -> WeatherReading | None:
    try:
        live_weather = await CwaProvider(settings.cwa_api_key).current_weather_nearest(location)
        if live_weather:
            return live_weather
    except Exception:
        pass

    if any(
        item is not None
        for item in (payload.wind_speed, payload.wind_direction, payload.rain_probability)
    ):
        return WeatherReading(
            source="manual-weather-fallback",
            wind_speed=payload.wind_speed,
            wind_direction=payload.wind_direction,
            rain_probability=payload.rain_probability,
        )
    return None
