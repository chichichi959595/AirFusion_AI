import unittest

from app.core.geo import Location

try:
    import httpx  # noqa: F401
except ModuleNotFoundError:
    httpx = None

if httpx:
    from app.providers.cwa import CwaProvider


class CwaProviderTests(unittest.TestCase):
    def test_parse_station_extracts_live_weather_fields(self) -> None:
        if httpx is None:
            self.skipTest("httpx is not installed in this Python environment")

        station = {
            "StationName": "臺北",
            "ObsTime": {"DateTime": "2026-04-30T14:00:00+08:00"},
            "GeoInfo": {
                "Coordinates": [
                    {
                        "CoordinateName": "WGS84",
                        "StationLatitude": "25.0377",
                        "StationLongitude": "121.5149",
                    }
                ]
            },
            "WeatherElement": {
                "WindDirection": "45.0",
                "WindSpeed": "3.2",
                "AirTemperature": "27.5",
                "RelativeHumidity": "68",
                "Now": {"Precipitation": "0.0"},
            },
        }

        reading = CwaProvider(api_key="test")._parse_station(
            station,
            Location(24.996222, 121.576211),
        )

        self.assertIsNotNone(reading)
        assert reading is not None
        self.assertEqual(reading.source, "CWA observation 臺北")
        self.assertEqual(reading.wind_direction, "NE")
        self.assertEqual(reading.wind_speed, 3.2)
        self.assertEqual(reading.humidity, 68)
        self.assertGreater(reading.distance_km or 0, 0)


if __name__ == "__main__":
    unittest.main()
