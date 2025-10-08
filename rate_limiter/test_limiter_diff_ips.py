import requests
import random

print("Starting burst of 24 requests from multiple simulated IPs...")

# A list of fake client IPs to simulate different users
client_ips = [
    "10.0.0.1",
    "20.20.20.2",
    "30.30.30.3"
]

for i in range(1, 25):
    try:
        simulated_ip = random.choice(client_ips)
        headers = {
            "X-Forwarded-For": simulated_ip
        }

        response = requests.get("http://localhost:8000/limited", headers=headers, timeout=5)

        print(f"Request {i} from {simulated_ip:<10}: Status {response.status_code} {response.reason}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e} - Request {i}")

    # No sleep to simulate a true burst
    # time.sleep(0.1)

print("\nFinished.")
