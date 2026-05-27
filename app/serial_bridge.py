from __future__ import annotations

import argparse
import asyncio
import json
import time
from collections.abc import Sequence
from typing import Any

import httpx


DEFAULT_LOCATION = {
    "lat": 24.996222,
    "lon": 121.576211,
    "location_label": "Taipei Wenshan",
    "language": "zh-Hant",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Forward Arduino Uno PMS5003T serial JSON to AirFusion AI.")
    parser.add_argument("--port", help="Arduino serial port, for example COM7. If omitted, the first Arduino-like port is used.")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--url", default="http://127.0.0.1:8000/sensor/report")
    parser.add_argument("--timeout", type=float, default=45.0, help="Backend POST timeout in seconds.")
    parser.add_argument("--list-ports", action="store_true", help="List detected serial ports and exit.")
    parser.add_argument("--lat", type=float, default=DEFAULT_LOCATION["lat"])
    parser.add_argument("--lon", type=float, default=DEFAULT_LOCATION["lon"])
    parser.add_argument("--location-label", default=DEFAULT_LOCATION["location_label"])
    parser.add_argument("--language", default=DEFAULT_LOCATION["language"])
    return parser.parse_args()


def list_ports(serial_module: Any) -> list[Any]:
    from serial.tools import list_ports as serial_list_ports

    ports = list(serial_list_ports.comports())
    if not ports:
        print("No serial ports detected.")
        return []

    print("Detected serial ports:")
    for port in ports:
        print(f"  {port.device}: {port.description}")
    return ports


def choose_port(ports: Sequence[Any]) -> str:
    preferred_words = ("arduino", "ch340", "wch", "usb serial", "usb-serial")
    for port in ports:
        description = str(port.description).lower()
        if any(word in description for word in preferred_words):
            return str(port.device)
    return str(ports[0].device)


async def post_report(url: str, report: dict[str, Any], args: argparse.Namespace) -> None:
    payload = {
        "lat": args.lat,
        "lon": args.lon,
        "location_label": args.location_label,
        "language": args.language,
        **report,
    }
    print(f"POST payload: pm25={payload.get('pm25')} pm10={payload.get('pm10')} url={url}")
    async with httpx.AsyncClient(timeout=args.timeout) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        result = response.json()

    print(
        "POST ok:",
        f"scenario={result.get('scenario')}",
        f"source={result.get('message_source')}",
        f"aqi={result.get('regional_aqi')}",
    )


async def main() -> None:
    args = parse_args()
    try:
        import serial
        from serial import SerialException
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing dependency: pyserial. Install it with:\n"
            '  python -m pip install pyserial\n'
            "Then run this bridge again."
        ) from exc

    ports = list_ports(serial)
    if args.list_ports:
        return

    if not args.port and not ports:
        raise SystemExit("No serial ports detected. Plug in the Arduino Uno and try again.")

    port = args.port or choose_port(ports)
    print(f"Reading Arduino on {port} at {args.baud} baud.")
    print(f"Forwarding reports to {args.url}.")

    try:
        arduino = serial.Serial(port, args.baud, timeout=2)
    except SerialException as exc:
        raise SystemExit(
            f"Could not open {port}: {exc}\n"
            "Close Arduino IDE Serial Monitor/Serial Plotter, unplug and replug the Uno, "
            "then run this bridge again."
        ) from exc

    print(f"Opened {port}. Waiting for Uno JSON...")
    last_seen_at = time.monotonic()
    with arduino:
        while True:
            line = arduino.readline().decode("utf-8", errors="replace").strip()
            if not line:
                if time.monotonic() - last_seen_at >= 5:
                    print("No serial JSON yet. If this keeps repeating, press Uno RESET and check PMS5003T wiring.")
                    last_seen_at = time.monotonic()
                continue

            last_seen_at = time.monotonic()
            print("SERIAL:", line)
            try:
                report = json.loads(line)
            except json.JSONDecodeError:
                continue

            if report.get("status"):
                print(f"UNO status: {report['status']}")
                continue

            if "pm25" not in report:
                continue

            try:
                await post_report(args.url, report, args)
            except httpx.ConnectError as exc:
                print(f"POST failed: cannot connect to backend at {args.url}. Is uvicorn running? {exc}")
            except httpx.HTTPStatusError as exc:
                print(f"POST failed: backend returned HTTP {exc.response.status_code}: {exc.response.text}")
            except httpx.TimeoutException as exc:
                print(f"POST failed: backend timeout after {args.timeout:g} seconds: {exc}")
            except Exception as exc:
                print(f"POST failed: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
