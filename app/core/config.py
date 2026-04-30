from dataclasses import dataclass
from functools import lru_cache
import os

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    load_dotenv = None


if load_dotenv:
    load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = "AirFusion AI"
    app_env: str = "development"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5.4-nano"
    moenv_api_key: str | None = None
    cwa_api_key: str | None = None
    mqtt_broker_url: str = "mqtt://broker.emqx.io:1883"
    mqtt_topic: str = "city/taipei/wenshan/sensor01/pm25"
    default_lat: float = 24.996222
    default_lon: float = 121.576211
    default_radius_km: float = 3.0


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "AirFusion AI"),
        app_env=os.getenv("APP_ENV", "development"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.4-nano"),
        moenv_api_key=os.getenv("MOENV_API_KEY") or None,
        cwa_api_key=os.getenv("CWA_API_KEY") or None,
        mqtt_broker_url=os.getenv("MQTT_BROKER_URL", "mqtt://broker.emqx.io:1883"),
        mqtt_topic=os.getenv("MQTT_TOPIC", "city/taipei/wenshan/sensor01/pm25"),
        default_lat=float(os.getenv("DEFAULT_LAT", "24.996222")),
        default_lon=float(os.getenv("DEFAULT_LON", "121.576211")),
        default_radius_km=float(os.getenv("DEFAULT_RADIUS_KM", "3")),
    )
