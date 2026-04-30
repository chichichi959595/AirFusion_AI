from app.domain import FusionResult
from app.services.advisor import LANGUAGE_NAMES


def build_air_quality_prompt(result: FusionResult, *, language: str = "zh-Hant") -> str:
    weather = result.weather
    neighborhood = result.neighborhood
    regional = result.regional
    language_name = LANGUAGE_NAMES.get(language, LANGUAGE_NAMES["zh-Hant"])

    return "\n".join(
        [
            f"<target_language>{language_name}</target_language>",
            "<role>You are an air-quality and personal exposure risk analyst.</role>",
            "<task>Use multi-scale data to identify likely pollution source, health risk, and immediate actions.</task>",
            "<local>",
            f"source={result.local.source}",
            f"pm25={result.local.pm25}",
            f"temperature={result.local.temperature}",
            f"humidity={result.local.humidity}",
            "</local>",
            "<neighborhood>",
            f"source={neighborhood.source if neighborhood else None}",
            f"pm25={neighborhood.pm25 if neighborhood else None}",
            f"distance_km={neighborhood.distance_km if neighborhood else None}",
            "</neighborhood>",
            "<regional>",
            f"source={regional.source if regional else None}",
            f"pm25={regional.pm25 if regional else None}",
            f"aqi={regional.aqi if regional else None}",
            "</regional>",
            "<weather>",
            f"source={weather.source if weather else None}",
            f"wind_speed={weather.wind_speed if weather else None}",
            f"wind_direction={weather.wind_direction if weather else None}",
            f"rain_probability={weather.rain_probability if weather else None}",
            f"precipitation={weather.precipitation if weather else None}",
            f"humidity={weather.humidity if weather else None}",
            f"station_distance_km={weather.distance_km if weather else None}",
            "</weather>",
            "<fusion>",
            f"scenario={result.scenario}",
            f"confidence={result.confidence}",
            f"risk_aqi={result.risk_aqi}",
            f"risk_band={result.risk_band}",
            "</fusion>",
            "<output_format>Return three numbered items: source judgment, health risk, and immediate recommendations.</output_format>",
        ]
    )
