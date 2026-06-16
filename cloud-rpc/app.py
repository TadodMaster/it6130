import requests

BASE = "https://thingsboard.cloud"

USERNAME = "tadod.de@gmail.com"
PASSWORD = "Wup9jG858:Ujqgr"

# Bước 1: Đăng nhập, lấy JWT
resp = requests.post(f"{BASE}/api/auth/login",
                     json={"username": USERNAME, "password": PASSWORD})
jwt = resp.json()["token"]
headers = {"X-Authorization": f"Bearer {jwt}"}
print("Đăng nhập thành công!")

# Bước 2: Lấy danh sách thiết bị để tìm deviceId
r = requests.get(f"{BASE}/api/tenant/devices?page=0&pageSize=10", headers=headers)
devices = r.json()["data"]
for d in devices:
    print(f"  - {d['name']}  id={d['id']['id']}")

# deviceId của thiết bị
DEVICE_ID = "430b9670-64e4-11f1-ad38-35390c349091"

# Two-way
body = {"method": "getTemperature", "params": None}

resp = requests.post(f"{BASE}/api/rpc/twoway/{DEVICE_ID}",
                     json=body, headers=headers,
                     timeout=10)  # chờ tối đa 10 giây
print("Kết quả từ thiết bị:", resp.json())