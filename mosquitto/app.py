import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "iot/sensors")
DEVICE_ID = os.getenv("DEVICE_ID", "sensor-01")
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "2"))


def create_sensor_data():
    # Generate simulated sensor values.
    temperature = round(random.uniform(25.0, 35.0), 2)
    humidity = round(random.uniform(50.0, 90.0), 2)

    data = {
        "device_id": DEVICE_ID,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return data


def main():
    # Create an MQTT client.
    client = mqtt.Client(client_id=DEVICE_ID)

    print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} ...")
    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)

    print(f"Publishing data to topic: {MQTT_TOPIC}")
    while True:
        data = create_sensor_data()
        payload = json.dumps(data)
        result = client.publish(MQTT_TOPIC, payload)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            print(f"Published: {payload}")
        else:
            print(f"Failed to publish message. Error code: {result.rc}")
        time.sleep(PUBLISH_INTERVAL)


if __name__ == "__main__":
    main()
