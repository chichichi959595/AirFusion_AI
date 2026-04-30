import unittest

from app.core.geo import Location
from app.domain import AirReading
from app.services.fusion import FusionService


class FusionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = FusionService()
        self.location = Location(24.996222, 121.576211)

    def test_detects_indoor_source(self) -> None:
        result = self.service.analyze(
            location=self.location,
            local=AirReading(source="local", pm25=45),
            neighborhood=AirReading(source="airbox", pm25=20),
            regional=AirReading(source="moenv", pm25=18, aqi=62),
        )

        self.assertEqual(result.scenario, "indoor_source")
        self.assertIn("室內", result.summary)

    def test_detects_neighborhood_hotspot(self) -> None:
        result = self.service.analyze(
            location=self.location,
            local=AirReading(source="local", pm25=50),
            neighborhood=AirReading(source="airbox", pm25=52),
            regional=AirReading(source="moenv", pm25=25, aqi=70),
        )

        self.assertEqual(result.scenario, "neighborhood_hotspot")


if __name__ == "__main__":
    unittest.main()
