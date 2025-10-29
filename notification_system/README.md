# FastAPI Notification System

A modular, production-ready notification system built with FastAPI, supporting email notifications with
click tracking, analytics, rate limiting, retries, and graceful worker management.

***

## Features

- FastAPI REST endpoint for notification intake with API key authentication.
- In-memory rate limiting per API key.
- User and device info caching with SQLite persistence.
- Async background worker for processing notification queue.
- SMTP email sending with dynamic click tracking URLs.
- Retry logic for failed notifications.
- Notification logging and analytics with database persistence.
- Click tracking endpoint to monitor user engagement.
- Graceful worker startup and shutdown integrated with FastAPI lifecycle.
- Comprehensive logging for all modules.

***

## Project Structure

```
notification_system/
│
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI app entrypoint, routes
│   ├── api_models/
│   │   ├── __init__.py
│   │   ├── models.py            # User and device model(s)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py            # API key authentication logic
│   │   ├── rate_limiter.py    # Rate limit logic
│   │   ├── cache.py           # Cache layer
│   │   ├── worker.py          # Worker and queue logic
│   │   ├── notification_sender.py  # SMTP and email sender
│   │   ├── analytics.py       # Analytics, delivery reporting
│   ├── logging/
│   │   ├── __init__.py
│   │   ├── logging_config.py  # Logger setup and config
│   ├── templates/             # (Optional)
│   │   └── notification_email.txt  # Email templates (Optional)
├── setup_user.py              # Database and test user setup script
├── requirements.txt           # Python dependencies
├── .env                       # (gitignored) environment variables
├── README.md                  # Project description
├── logs/
│   └── ...                    # Log files per module
```

***

## Getting Started

### Prerequisites

- Python 3.11
- SMTP email account (Gmail with App Password recommended) or Mailtrap for testing
- SQLite (default) or configure alternative DB

### Installation

1.  Clone the repo:

    ```bash
    git clone https://github.com/pritambhutada5/system_design.git
    cd notification_system
    ```

2.  Install dependencies:

    ```bash
    pip install fastapi uvicorn sqlalchemy python-dotenv
    ```

3.  Configure SMTP credentials in `.env` file:

    ```
    SMTP_SERVER="smtp.gmail.com"
    SMTP_PORT=587
    SMTP_USER=""
    SMTP_PASSWORD=""
    API_KEYS="<key>:<value>"
    ```

4.  Add test users by running your setup script:

    ```bash
    python setup_user.py
    ```

## Running the Application

Start the FastAPI server (worker auto-starts):

```bash
  uvicorn app.main:app --reload
```

Open the interactive API docs at:

    [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Use the `/notify` POST endpoint with your API key and JSON body including `email` and `message`.
The system queues notifications and sends emails asynchronously with click tracking.

***

## Features in Detail

-   **Authentication & Rate Limiting**: Protect endpoints with API key and limit request rate.
-   **Worker Thread**: Processes queued notification tasks, sending emails and handling retries.
-   **Email with Click Tracking**: Emails contain unique links for tracking clicks via API.
-   **Logging & Analytics**: All activity logged with details stored in SQLite and log files.
-   **Graceful Shutdown**: Worker stops cleanly on server shutdown using sentinels.
-   **Retry Logic**: Failed sends are retried up to configurable limit.

***

## Extending the System

-   Add richer notification templates under `templates/`.
-   Switch SMTP to popular services or integrate SMS gateways.
-   Replace SQLite with full-fledged RDBMS or NoSQL backend.
-   Add WebSocket or SSE real-time notification support.
-   Build dashboards or reports from notification analytics.

---