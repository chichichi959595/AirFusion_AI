import unittest

from app.core.geo import Location
from app.domain import AirReading
from app.services.advisor import build_rule_based_message
from app.services.fusion import FusionService


class AdvisorTests(unittest.TestCase):
    def test_rule_based_message_is_user_readable(self) -> None:
        result = FusionService().analyze(
            location=Location(24.996222, 121.576211),
            local=AirReading(source="arduino", pm25=45),
            neighborhood=AirReading(source="airbox", pm25=20),
            regional=AirReading(source="moenv", pm25=18, aqi=62),
        )

        message = build_rule_based_message(result)

        self.assertIn("室內 PM2.5", message)
        self.assertIn("建議", message)


if __name__ == "__main__":
    unittest.main()
