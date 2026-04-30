from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse

import paho.mqtt.client as mqtt

from app.domain import AirReading


ReadingHandler = Callable[[AirReading], None]


@dataclass
class MqttIngestor:
    broker_url: str
    topic: str
    client_id: str = "airfusion-ai-ingestor"

    def start(self, on_reading: ReadingHandler) -> mqtt.Client:
        parsed = urlparse(self.broker_url)
        host = parsed.hostname or self.broker_url
        port = parsed.port or 1883
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id)

        def handle_message(_client: mqtt.Client, _userdata: object, message: mqtt.MQTTMessage) -> None:
            payload = json.loads(message.payload.decode("utf-8"))
            on_reading(
                AirReading(
                    source=str(payload.get("source") or self.topic),
                    pm25=_as_float(payload.get("pm25")),
                    pm10=_as_float(payload.get("pm10")),
                    temperature=_as_float(payload.get("temperature")),
                    humidity=_as_float(payload.get("humidity")),
                    raw=payload,
                )
            )

        client.on_message = handle_message
        client.connect(host, port, keepalive=60)
        client.subscribe(self.topic, qos=1)
        client.loop_start()
        return client


def _as_float(value: object) -> float | None:
    if value in {None, ""}:
        return None
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
