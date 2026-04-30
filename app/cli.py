import json

from app.core.geo import Location
from app.domain import AirReading, WeatherReading
from app.services.fusion import FusionService
from app.services.prompting import build_air_quality_prompt


def main() -> None:
    result = FusionService().analyze(
        location=Location(24.996222, 121.576211, "Taipei Wenshan"),
        local=AirReading(source="sensor01", pm25=45, temperature=26.5, humidity=58),
        neighborhood=AirReading(source="airbox-nearby", pm25=20, distance_km=0.8),
        regional=AirReading(source="MOENV Muzha", pm25=18, aqi=62),
        weather=WeatherReading(source="CWA Taipei", wind_speed=3.2, wind_direction="NE", rain_probability=20),
    )
    print(
        json.dumps(
            {
                "scenario": result.scenario,
                "confidence": result.confidence,
                "summary": result.summary,
                "recommendations": result.recommendations,
                "llm_prompt": build_air_quality_prompt(result),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
