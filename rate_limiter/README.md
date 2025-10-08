***
# Distributed Token Bucket Rate Limiter with FastAPI and Redis

This project implements a high-performance, **distributed token bucket rate limiter** as a middleware for the **FastAPI** framework. It uses **Redis** as a centralized backend to ensure that rate limits are applied consistently across multiple application instances, making it suitable for scalable, production-grade services.

The core logic is executed via a **Redis Lua script** to guarantee atomic operations, preventing race conditions in a high-concurrency environment.

## Features

-   **Token Bucket Algorithm**: A flexible and widely-used algorithm that allows for bursts of traffic before enforcing a limit.
-   **Distributed & Scalable**: Uses a centralized Redis backend, making it effective across any number of application servers.
-   **Atomic Operations**: Employs a Lua script to ensure that checking and consuming tokens is an atomic, race-condition-free operation.
-   **Fully Asynchronous**: Built on FastAPI and `redis.asyncio` for high-throughput, non-blocking performance.
-   **Externalized Configuration**:
    -   Environment variables (`.env` file) for sensitive data like Redis connection details.
    -   A `rate_limits.json` file to define rate-limiting rules, which can be modified without changing the code.
-   **Containerized with Docker**: Comes with a `Dockerfile` and `docker-compose.yml` for easy, reproducible, one-command setup of the entire application stack.

***

## Project Structure

```
/rate_limiter
|-- app/
|   |-- __init__.py
|   |-- main.py               # FastAPI application entrypoint and middleware registration
|   |-- rate_limiter.py       # The core middleware logic and Lua script
|   |-- config.py             # Loads and manages configuration
|   |-- logging_config.py     # Sets up production-ready logging
|
|-- .env                      # Environment variables (e.g., Redis host) - NOT committed
|-- rate_limits.json          # Rate limiting rules (e.g., capacity, refill rate)
|-- requirements.txt          # Python package dependencies
|-- test_limiter.py           # A simple Python script for manually testing the rate limiter
|
|-- Dockerfile                # Instructions to build the FastAPI application image
|-- docker-compose.yml        # Defines and runs the multi-container (app + Redis) setup
|-- README.md                 # This file
```

***

## Getting Started

### Prerequisites

-   Docker
-   Docker Compose

### Quickstart with Docker Compose (Recommended)

This is the easiest and most reliable way to run the entire application stack.

1.  **Clone the repository** (if you haven't already).

2.  **Build and run the services**:
    From the project's root directory, run:
    ```bash
    docker-compose up --build
    ```
    This command will:
    -   Build the Docker image for the FastAPI application.
    -   Start a Redis container.
    -   Start the FastAPI application container and network it with the Redis container.

3.  **Access the application**:
    The API will be available at `http://localhost:8000`.

4.  **Test the rate limiter**:
    Open a new terminal and run the provided test script:
    ```bash
    python test_limiter.py
    ```
    You will see the output of the requests, including the `429 Too Many Requests` responses once the limit is exceeded.

5.  **Stop the services**:
    Press `CTRL+C` in the terminal where `docker-compose` is running, then run `docker-compose down` to clean up the containers and network.

### Running Locally (Without Docker)

1.  **Set up a Python virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # or
    # venv\Scripts\activate    # On Windows
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Start a Redis server**:
    Ensure you have a Redis instance running on `localhost:6379`.

4.  **Run the FastAPI application**:
    ```bash
    uvicorn app.main:app --reload
    ```

***

## Configuration

The application is configured through two primary files:

#### 1. `.env` file
Stores environment-specific variables. Create this file in the project root.
```
REDIS_HOST=redis        # Use 'redis' for Docker Compose, 'localhost' for local runs
REDIS_PORT=6379
REDIS_DB=0
RATE_LIMIT_RULES_PATH=rate_limits.json
```

#### 2. `rate_limits.json` file
Defines the rules for the rate limiter. You can add more rules and modify the middleware to apply them to different endpoints.
```json
{
  "default": {
    "capacity": 20,
    "refill_rate": 5
  },
  "special_path": {
    "capacity": 50,
    "refill_rate": 10
  }
}
```

***

## How It Works

The rate limiter is implemented as a FastAPI middleware that intercepts every incoming request.

1.  It identifies the client using their IP address (prioritizing the `X-Forwarded-For` header).
2.  For each unique client, it uses a Redis Hash to store their token bucket state (`tokens` and `timestamp`).
3.  A **Lua script** is executed on the Redis server to atomically:
    -   Calculate how many tokens to refill based on the elapsed time.
    -   Check if enough tokens are available for the current request.
    -   Consume a token if the request is allowed.
    -   Return the result (allowed/denied) and the remaining token count.
4.  If the request is allowed, it proceeds to the endpoint. If denied, the middleware immediately returns a `429 Too Many Requests` response.

Using a Lua script is essential for preventing race conditions and ensuring the integrity of the rate limit in a distributed, high-concurrency system.