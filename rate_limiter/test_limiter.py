import requests
import time


print("Starting burst of 24 requests to http://localhost:8000/limited...")

for i in range(1, 25):
    try:
        response = requests.get("http://localhost:8000/limited", timeout=5, stream=True)

        try:
            version = response.raw.version
            http_version = f"HTTP/{version // 10}.{version % 10}"
        except (AttributeError, TypeError):
            http_version = "HTTP/?.?"

        print(f"{http_version} {response.status_code} {response.reason} - Request {i}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e} - Request {i}")

    """
    -- By removing time.sleep(0.1), your test_limiter.py script now sends requests as fast as the Python process and your local network will allow. 
    This creates a true "burst" scenario where there is virtually no time between requests for new tokens to be generated.
    -- Behavior with time.sleep(0.1) showed the refill mechanism working over small time gaps
    """
    time.sleep(0.1)

print("\nFinished.")
