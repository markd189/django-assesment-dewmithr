# Device Monitor (Django + DRF)

A simple device monitoring API that accepts telemetry and generates alerts based on per-device alert rules.

## Prerequisites

- Python 3.x
- pipenv
- PostgreSQL (local install)

## Setup (step-by-step)

### 1) Clone / open the project

Open a terminal in the project root:

```bash
D:\Django tutorial\device_monitor
```

### 2) Install Python dependencies

```bash
pipenv install
```

If you do not have `pipenv`:

```bash
pip install pipenv
```

### 3) Create the PostgreSQL database and user

Connect as the `postgres` superuser:

```bash
psql -U postgres -h 127.0.0.1 -p 5432
```

Run the following SQL:

```sql
CREATE DATABASE device_monitor;
CREATE USER device_monitor_user WITH PASSWORD 'device_monitor_pass';
GRANT ALL PRIVILEGES ON DATABASE device_monitor TO device_monitor_user;

-- Ensure the app user can create tables in the public schema
ALTER DATABASE device_monitor OWNER TO device_monitor_user;
\c device_monitor
GRANT USAGE, CREATE ON SCHEMA public TO device_monitor_user;
ALTER SCHEMA public OWNER TO device_monitor_user;
```

Exit:

```sql
\q
```

### 4) Configure database connection

This project is configured to use PostgreSQL in `device_monitor/settings.py`.

Default connection values:

- DB: `device_monitor`
- User: `device_monitor_user`
- Password: `device_monitor_pass`
- Host: `127.0.0.1`
- Port: `5432`

## How to run migrations

```bash
pipenv run python manage.py migrate
```

## How to create the admin user

```bash
pipenv run python manage.py createsuperuser
```

## Run the app

```bash
pipenv run python manage.py runserver
```

Useful URLs:

- Admin UI: `http://127.0.0.1:8000/admin/`
- OpenAPI schema: `http://127.0.0.1:8000/api/schema/`
- Swagger UI docs: `http://127.0.0.1:8000/api/docs/`

## Sample API calls (curl)

Base URL:

```text
http://127.0.0.1:8000
```

### 1) Create a device (authenticated)

The devices API requires authentication (`IsAuthenticated`).

The simplest way to test locally:

1. Log in at `/admin/` in a browser.
2. Use the same browser session to access DRF browsable API (if enabled).

If you prefer curl-based auth, add an auth method (e.g., token auth) and then call the endpoint.

Endpoint:

```text
POST /api/devices/
```

Example body:

```json
{
  "name": "Office Sensor 1",
  "type": "SENSOR",
  "location": "HQ Floor 2",
  "is_active": true
}
```

### 2) Send telemetry (ingest)

Endpoint:

```text
POST /api/telemetry/
```

Example curl:

```bash
curl -X POST http://127.0.0.1:8000/api/telemetry/ \
  -H "Content-Type: application/json" \
  -d "{\"device_id\":\"PUT-DEVICE-UUID-HERE\",\"status\":\"ONLINE\",\"cpu\":10.5,\"memory\":34.2,\"temperature\":40.0}"
```

Notes:

- `device_id` must be the UUID from `Device.device_id` (visible in the Django admin Device list/detail page).
- `temperature` is optional.

## Using the UI (Admin)

- Log in to `/admin/`
- Create a `Device`
- Create `AlertRule` entries for that device
- POST telemetry to `/api/telemetry/`
- Check generated `Alert` entries in the admin

## Design notes

### Models

- **Device**
  - User-owned device with a public-facing UUID (`device_id`) used by telemetry ingestion.
- **Telemetry**
  - Incoming status and performance metrics for a device.
- **AlertRule**
  - Per-device rules (CPU/MEMORY/TEMP thresholds, OFFLINE status).
- **Alert**
  - Generated when telemetry violates a rule.

### Alert logic

- New telemetry is processed via a Django `post_save` signal receiver.
- For each active `AlertRule` on the device, telemetry values are checked.
- An `Alert` is created when a rule is violated.
- Duplicate prevention:
  - A new alert for the same `device + rule` is created **only if there is no existing `OPEN` alert** for that rule.
  - Once the previous alert is **ACK** or **RESOLVED**, new violations can create a new alert again.

## Roles / Permissions summary

- **Superuser (admin)**
  - Full access to all objects.
- **Staff user (normal user with admin dashboard access)**
  - Restricted to their own devices, rules, telemetry, and alerts in the admin.
  - Can acknowledge alerts (admin action) for their own devices.
