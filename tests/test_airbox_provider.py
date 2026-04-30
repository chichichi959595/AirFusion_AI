import unittest

from app.core.geo import Location

try:
    import httpx  # noqa: F401
except ModuleNotFoundError:
    httpx = None

if httpx:
    from app.providers.airbox import AirBoxProvider


class AirBoxProviderTests(unittest.TestCase):
    def test_parse_feed_preserves_zero_pm25_and_uses_station_label(self) -> None:
        if httpx is None:
            self.skipTest("httpx is not installed in this Python environment")

        feed = {
            "SiteName": "市立興隆國小(2018)",
            "device_id": "74DA38F7C524",
            "gps_lat": 24.998,
            "gps_lon": 121.558,
            "s_d0": 0.0,
            "s_t0": 19.87,
            "s_h0": 100.0,
        }

        reading = AirBoxProvider()._parse_feed(feed, Location(24.996222, 121.576211))

        self.assertIsNotNone(reading)
        assert reading is not None
        self.assertEqual(reading.pm25, 0.0)
        self.assertEqual(reading.source, "AirBox 市立興隆國小(2018)")
        self.assertEqual(reading.location.label, "市立興隆國小(2018)")
        self.assertGreater(reading.distance_km or 0, 0)


if __name__ == "__main__":
    unittest.main()
