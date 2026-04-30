import argparse
import asyncio
import json

from app.core.geo import Location
from app.domain import AirReading, WeatherReading
from app.services.advisor import AdvisorService
from app.services.fusion import FusionService
from app.services.prompting import build_air_quality_prompt


async def run(pm25: float, neighborhood_pm25: float, regional_pm25: float, aqi: int) -> None:
    result = FusionService().analyze(
        location=Location(24.996222, 121.576211, "Taipei Wenshan"),
        local=AirReading(source="arduino-sensor01", pm25=pm25, temperature=27.0, humidity=60),
        neighborhood=AirReading(source="airbox-sample", pm25=neighborhood_pm25, distance_km=0.8),
        regional=AirReading(source="moenv-sample", pm25=regional_pm25, aqi=aqi),
        weather=WeatherReading(source="cwa-sample", wind_speed=3.2, wind_direction="NE", rain_probability=20),
    )
    prompt = build_air_quality_prompt(result)
    message, source = await AdvisorService().create_user_message(result, prompt)
    print(
        json.dumps(
            {
                "ok": True,
                "message_source": source,
                "scenario": result.scenario,
                "message": message,
                "summary": result.summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate an Arduino air-quality sensor report.")
    parser.add_argument("--pm25", type=float, default=45)
    parser.add_argument("--neighborhood-pm25", type=float, default=20)
    parser.add_argument("--regional-pm25", type=float, default=18)
    parser.add_argument("--aqi", type=int, default=62)
    args = parser.parse_args()
    asyncio.run(run(args.pm25, args.neighborhood_pm25, args.regional_pm25, args.aqi))


if __name__ == "__main__":
    main()
