# it6130

Lập trình và ảo hóa cho IoT — bài thực hành thu thập thông số hệ thống và truyền qua MQTT.

## Giới thiệu

Dự án gồm hai thành phần chạy trong container Docker:

- **`system-monitor-app/`** — ứng dụng Python thu thập thông số hệ thống (CPU, RAM, ổ đĩa) bằng [`psutil`](https://pypi.org/project/psutil/) và publish định kỳ lên một topic MQTT dưới dạng JSON.
- **`mosquitto/`** — MQTT broker dựa trên [Eclipse Mosquitto](https://mosquitto.org/) dùng để nhận và trung chuyển dữ liệu.

## Kiến trúc

```
┌─────────────────────┐     publish (JSON)     ┌──────────────────┐
│ system-monitor-app  │ ─────────────────────► │ Mosquitto broker │
│  (psutil + paho)    │   topic: system/info   │   (port 1883)    │
└─────────────────────┘                        └──────────────────┘
```

Ứng dụng đọc các thông số mỗi `PUBLISH_INTERVAL` giây và gửi payload JSON, ví dụ:

```json
{
  "device_id": "system-monitor-01",
  "cpu_percent": 12.5,
  "cpu_count": 8,
  "ram_percent": 63.2,
  "ram_used_mb": 10123.45,
  "ram_total_mb": 16000.00,
  "disk_percent": 48.0,
  "disk_used_gb": 230.12,
  "disk_total_gb": 480.00,
  "boot_time": "2026-06-14T01:00:00+00:00",
  "timestamp": "2026-06-14T03:25:10+00:00"
}
```

## Cấu hình

Ứng dụng được cấu hình qua biến môi trường (xem `system-monitor-app/system_app.py`):

| Biến               | Mặc định            | Mô tả                                   |
| ------------------ | ------------------- | --------------------------------------- |
| `MQTT_BROKER`      | `localhost`         | Địa chỉ MQTT broker                     |
| `MQTT_PORT`        | `1883`              | Cổng MQTT broker                        |
| `MQTT_TOPIC`       | `system/info`       | Topic để publish dữ liệu                |
| `DEVICE_ID`        | `system-monitor-01` | Định danh thiết bị (cũng là client id)  |
| `PUBLISH_INTERVAL` | `2`                 | Khoảng thời gian giữa các lần gửi (giây)|

Broker dùng cấu hình tối thiểu trong `mosquitto/config/mosquitto.conf`:

```
listener 1883
allow_anonymous true
```

## Yêu cầu

- [Docker](https://www.docker.com/)
- Python >= 3.10 (nếu chạy trực tiếp không qua Docker)

## Chạy bằng Docker

### 1. Khởi động Mosquitto broker

```bash
docker run -it --rm --name mqtt-broker \
  -p 1883:1883 \
  -v "$PWD/mosquitto/config:/mosquitto/config:ro" \
  eclipse-mosquitto:latest
```

(Tham khảo `mosquitto/docker.sh`.)

### 2. Build và chạy ứng dụng giám sát

```bash
cd system-monitor-app
docker build -t system-monitor-app .
docker run --rm \
  -e MQTT_BROKER=host.docker.internal \
  system-monitor-app
```

> Dùng `host.docker.internal` để container ứng dụng kết nối tới broker đang chạy trên máy host.

### 3. Kiểm tra dữ liệu

Subscribe vào topic để xem dữ liệu được publish:

```bash
docker run -it --rm eclipse-mosquitto:latest \
  mosquitto_sub -h host.docker.internal -t system/info
```

## Chạy trực tiếp (không Docker)

```bash
cd system-monitor-app
pip install -r requirements.txt
python system_app.py
```

## Cấu trúc thư mục

```
it6130/
├── system-monitor-app/      # Ứng dụng thu thập & publish thông số hệ thống
│   ├── system_app.py        # Mã nguồn chính
│   ├── config/              # mosquitto.conf cho ứng dụng
│   ├── Dockerfile
│   └── requirements.txt     # paho-mqtt, psutil
├── mosquitto/               # MQTT broker
│   ├── config/mosquitto.conf
│   ├── docker.sh            # Lệnh khởi động broker
│   ├── Dockerfile
│   └── requirements.txt
├── docs/                    # Báo cáo bài thực hành (PDF)
└── pyproject.toml
```
