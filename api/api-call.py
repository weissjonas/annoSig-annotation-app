import requests


API_URL = "https://95.217.13.152:8000"
# API_URL = "https://127.0.0.1:8000"

API_TOKEN = "0e2d70b1f642f85550adb7ff20656462"


try:
    resp = requests.post(
        f"{API_URL}/upload",
        headers={
            "Authorization": API_TOKEN,
        },
        json={"I": "break you"}, 
        verify="ssl/ca.pem"
    )
    resp.raise_for_status()
except requests.RequestException as err:
    print("Error:", err)