import sys
import paho.mqtt.client as mqtt
import json

# ThingsBoard > Device > Copy access token
TOKEN = "wRTSxPeesJflhtGUrNSl"
REQ_TOPIC = "v1/devices/me/rpc/request/+"

def on_connect(client, userdata, flags, rc, properties=None):
    print("Đã kết nối, đang chờ lệnh...")
    client.subscribe(REQ_TOPIC)

def on_message(client, userdata, msg):
    rid = msg.topic.split('/')[-1]
    cmd = json.loads(msg.payload)
    method = cmd["method"]
    params = cmd.get("params")

    print(f"[NHẬN LỆNH] method={method}  params={params}")

    # Xử lý từng lệnh
    if method == "setLight":
        result = {"ok": True, "light": params}
        
    elif method == "getTemperature":
        import random
        temp = round(random.uniform(24.0, 32.0), 1)  # giả lập cảm biến
        result = {"ok": True, "temperature": temp}

    else:
        result = {"ok": False, "error": "unknown method"}

    # Publish kết quả — bắt buộc cho two-way
    resp_topic = f"v1/devices/me/rpc/response/{rid}"
    client.publish(resp_topic, json.dumps(result))
    print(f"[TRẢ LỜI] {result}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.username_pw_set(TOKEN)
client.on_connect = on_connect
client.on_message = on_message

client.connect("thingsboard.cloud", 1883)
client.loop_forever()