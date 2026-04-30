import json
import time

from machine import UART
from umqtt.simple import MQTTClient

from secrets import MQTT_BROKER, MQTT_CLIENT_ID, MQTT_TOPIC, WIFI_PASSWORD, WIFI_SSID


uart = UART(2, baudrate=9600, tx=17, rx=16)


def connect_wifi():
    import network

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(0.5)
    return wlan


def read_pms5003():
    if uart.any() < 32:
        return None
    frame = uart.read(32)
    if not frame or frame[0] != 0x42 or frame[1] != 0x4D:
        return None
    pm10 = frame[10] * 256 + frame[11]
    pm25 = frame[12] * 256 + frame[13]
    pm100 = frame[14] * 256 + frame[15]
    return {"pm10": pm10, "pm25": pm25, "pm100": pm100}


def main():
    connect_wifi()
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, keepalive=60)
    client.connect()

    while True:
        reading = read_pms5003()
        if reading:
            payload = {
                "source": MQTT_CLIENT_ID,
                "pm25": reading["pm25"],
                "pm10": reading["pm10"],
                "timestamp": time.time(),
            }
            client.publish(MQTT_TOPIC, json.dumps(payload), qos=1)
        time.sleep(60)


main()
