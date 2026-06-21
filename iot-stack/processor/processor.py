import json
import os
import time
from datetime import datetime

import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point, WritePrecision


MQTT_BROKER = os.getenv("MQTT_BROKER", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "#")

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://influxdb:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "iot-token-123")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "iot-lab")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "iot_data")


def parse_timestamp(timestamp_text):
    if not timestamp_text:
        return None

    try:
        normalized = timestamp_text.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except Exception:
        return None


def get_measurement_name(topic):
    if topic == "iot/sensors":
        return "sensor_data"
    if topic == "system/info":
        return "system_info"
    return "mqtt_data"


def create_point(topic, data):
    measurement = get_measurement_name(topic)
    device_id = str(data.get("device_id", "unknown"))

    point = Point(measurement)
    point = point.tag("device_id", device_id)
    point = point.tag("topic", topic)

    timestamp = parse_timestamp(data.get("timestamp"))
    if timestamp is not None:
        point = point.time(timestamp, WritePrecision.NS)

    field_count = 0

    for key, value in data.items():
        if key in ["device_id", "timestamp"]:
            continue

        if isinstance(value, bool):
            point = point.field(key, value)
            field_count += 1
        elif isinstance(value, int):
            point = point.field(key, value)
            field_count += 1
        elif isinstance(value, float):
            point = point.field(key, value)
            field_count += 1
        elif isinstance(value, str):
            point = point.field(key, value)
            field_count += 1

    if field_count == 0:
        return None

    return point


def connect_influxdb():
    while True:
        try:
            client = InfluxDBClient(
                url=INFLUXDB_URL,
                token=INFLUXDB_TOKEN,
                org=INFLUXDB_ORG
            )
            health = client.health()
            print(f"InfluxDB health: {health.status}")
            write_api = client.write_api()
            return write_api
        except Exception as exc:
            print(f"Cannot connect to InfluxDB: {exc}")
            print("Retrying in 5 seconds ...")
            time.sleep(5)


write_api = connect_influxdb()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect to MQTT broker. Return code: {rc}")


def on_message(client, userdata, message):
    topic = message.topic

    try:
        payload_text = message.payload.decode("utf-8")
        data = json.loads(payload_text)
        point = create_point(topic, data)

        if point is None:
            print(f"Skipped message without valid fields: {payload_text}")
            return

        write_api.write(
            bucket=INFLUXDB_BUCKET,
            org=INFLUXDB_ORG,
            record=point
        )

        print(f"Written to InfluxDB: topic={topic}, payload={payload_text}")

    except Exception as exc:
        print(f"Failed to process message from topic {topic}: {exc}")


def main():
    mqtt_client = mqtt.Client(client_id="iot-data-processor")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    while True:
        try:
            print(f"Connecting to MQTT broker at {MQTT_BROKER}:{MQTT_PORT} ...")
            mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            mqtt_client.loop_forever()
        except Exception as exc:
            print(f"MQTT connection error: {exc}")
            print("Retrying in 5 seconds ...")
            time.sleep(5)


if __name__ == "__main__":
    main()