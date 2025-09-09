import requests
import socket
import platform
import json
import os
from env import CONFIG_ENV


API_URL = CONFIG_ENV["SEND_REPORT_API"]
API_KEY = CONFIG_ENV["API_KEY"]


def send_report(checks: dict):
    print("API_URL:", API_URL)
    payload = {"report": checks}
    headers = {"x-api-key": API_KEY}
    try:
        response = requests.post(API_URL, json=payload,headers=headers, timeout=10)
        if response.status_code == 200:
            print("Report sent successfully")
            return True
        else:
            print(f"Failed to send report: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ Error sending report: {e}")
        return False
