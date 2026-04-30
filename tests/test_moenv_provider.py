import unittest

from app.core.geo import Location

try:
    import httpx  # noqa: F401
except ModuleNotFoundError:
    httpx = None

if httpx:
    from app.providers.moenv import MoenvProvider, _records_from_payload


class MoenvProviderTests(unittest.TestCase):
    def test_parse_record_extracts_official_aqi_fields(self) -> None:
        if httpx is None:
            self.skipTest("httpx is not installed in this Python environment")

        record = {
            "sitename": "木柵",
            "county": "臺北市",
            "aqi": "62",
            "pm2.5": "18",
            "pm10": "30",
            "longitude": "121.576211",
            "latitude": "24.996222",
            "publishtime": "2026-04-30 14:00",
        }

        reading = MoenvProvider(api_key="test")._parse_record(
            record,
            origin=Location(24.996222, 121.576211),
        )

        self.assertIsNotNone(reading)
        assert reading is not None
        self.assertEqual(reading.source, "MOENV 木柵")
        self.assertEqual(reading.pm25, 18)
        self.assertEqual(reading.aqi, 62)
        self.assertEqual(reading.distance_km, 0)

    def test_records_from_payload_accepts_list_or_wrapped_records(self) -> None:
        if httpx is None:
            self.skipTest("httpx is not installed in this Python environment")

        records = [{"sitename": "木柵"}]

        self.assertEqual(_records_from_payload(records), records)
        self.assertEqual(_records_from_payload({"records": records}), records)
        self.assertEqual(_records_from_payload({"records": {}}), [])


if __name__ == "__main__":
    unittest.main()
