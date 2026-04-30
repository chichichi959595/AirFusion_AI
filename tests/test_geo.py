import unittest

from app.core.geo import Location, haversine_distance_km


class GeoTests(unittest.TestCase):
    def test_haversine_distance_between_muzha_and_guting(self) -> None:
        muzha = Location(24.996222, 121.576211)
        guting = Location(25.02025, 121.529889)

        distance = haversine_distance_km(muzha, guting)

        self.assertGreater(distance, 5.0)
        self.assertLess(distance, 6.0)


if __name__ == "__main__":
    unittest.main()
