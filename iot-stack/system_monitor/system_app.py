import json
import os
import socket
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import psutil


MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "system/info")
DEVICE_ID = os.getenv("DEVICE_ID", "system-monitor-01")
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "5"))


def create_system_info():
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "device_id": DEVICE_ID,
        "hostname": socket.gethostname(),
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_used_mb": round(memory.used / (1024 * 1024), 2),
        "memory_total_mb": round(memory.total / (1024 * 1024), 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024 * 1024 * 1024), 2),
        "disk_total_gb": round(disk.total / (1024 * 1024 * 1024), 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def connect_mqtt_client():
    client = mqtt.Client(client_id=DEVICE_ID)

    while True:
        try:
            print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} ...")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            print("Connected to MQTT broker.")
            return client
        except Exception as exc:
            print(f"Connection failed: {exc}")
            print("Retrying in 5 seconds ...")
            time.sleep(5)


def main():
    client = connect_mqtt_client()
    print(f"Publishing system information to topic: {MQTT_TOPIC}")

    while True:
        try:
            data = create_system_info()
            payload = json.dumps(data)
            result = client.publish(MQTT_TOPIC, payload)

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published: {payload}")
            else:
                print(f"Failed to publish message. Error code: {result.rc}")

            time.sleep(PUBLISH_INTERVAL)
        except Exception as exc:
            print(f"Runtime error: {exc}")
            client = connect_mqtt_client()


if __name__ == "__main__":
    main()
