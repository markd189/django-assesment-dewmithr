"""TEST-ONLY SCRIPT

This script is intended only to test the application by sending dummy telemetry
data to the running API.

Run this script in a separate terminal/process from the Django server.
"""

import requests
import time
import random

URL = "http://127.0.0.1:8000/api/telemetry/"
DEVICE_IDS = [
    "9ec50fc9-1ed6-46fd-9344-e1b38704f4b6",  # <-- Replace with real UUID #1
    "PUT-DEVICE-UUID-2-HERE",                # <-- Replace with real UUID #2
    "PUT-DEVICE-UUID-3-HERE",                # <-- Replace with real UUID #3
]


def generate_telemetry(device_id):
    return {
        "device_id": device_id,
        "status": "ONLINE",
        "cpu": round(random.uniform(10, 100), 2),
        "memory": round(random.uniform(10, 100), 2),
        "temperature": round(random.uniform(20, 90), 2),
    }


while True:
    device_id = random.choice(DEVICE_IDS)
    data = generate_telemetry(device_id)

    try:
        response = requests.post(URL, json=data)
        print("Sent:", data)
        print("Response:", response.status_code, response.text)
    except Exception as e:
        print("Error:", e)

    time.sleep(5)