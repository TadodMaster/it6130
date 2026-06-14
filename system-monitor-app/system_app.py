import json
import os
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
import psutil

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "system/info")
DEVICE_ID = os.getenv("DEVICE_ID", "system-monitor-01")
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "2"))


def create_system_data():
    # Collect real system metrics via psutil.
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    data = {
        "device_id": DEVICE_ID,
        # cpu_percent(interval=None) reports usage since the previous call,
        # so it is primed once in main() before the loop starts.
        "cpu_percent": psutil.cpu_percent(interval=None),
        "cpu_count": psutil.cpu_count(),
        "ram_percent": mem.percent,
        "ram_used_mb": round(mem.used / (1024 * 1024), 2),
        "ram_total_mb": round(mem.total / (1024 * 1024), 2),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "boot_time": datetime.fromtimestamp(
            psutil.boot_time(), timezone.utc
        ).isoformat(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return data


def main():
    # Create an MQTT client.
    client = mqtt.Client(client_id=DEVICE_ID)

    print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    # Prime cpu_percent so the first reading in the loop is meaningful
    # (the first call always returns 0.0).
    psutil.cpu_percent(interval=None)

    print(f"Publishing data to topic: {MQTT_TOPIC}")
    while True:
        data = create_system_data()
        payload = json.dumps(data)
        result = client.publish(MQTT_TOPIC, payload)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Published: {payload}")
        else:
            print(f"Failed to publish message. Error code: {result.rc}")
        time.sleep(PUBLISH_INTERVAL)


if __name__ == "__main__":
    main()
