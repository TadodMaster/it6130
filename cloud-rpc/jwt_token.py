import requests

BASE = "https://thingsboard.cloud"

r = requests.post(
    f"{BASE}/api/auth/login",
    json={
        "username": "tadod.de@gmail.com",
        "password": "Wup9jG858:Ujqgr"
    }
)

jwt = r.json()['token']

print(jwt)

h = {"X-Authorization": f"Bearer {jwt}"}

r = requests.get(f"{BASE}/api/tenant/devices?page=0&pageSize=10", headers=h)

for d in r.json()['data']:
    print(d['name'], d['id']['id'])