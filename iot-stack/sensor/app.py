import json
import os
import random
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "iot/sensors")
DEVICE_ID = os.getenv("DEVICE_ID", "sensor-01")
PUBLISH_INTERVAL = float(os.getenv("PUBLISH_INTERVAL", "2"))

def create_sensor_data():
    temperature = round(random.uniform(25.0, 35.0), 2)
    humidity = round(random.uniform(50.0, 90.0), 2)

    return {
        "device_id": DEVICE_ID,
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": datetime.now(timezone.utc).isoformat()
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
    print(f"Publishing sensor data to topic: {MQTT_TOPIC}")

    while True:
        try:
            data = create_sensor_data()
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
