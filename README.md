# Booking API

A REST API for reserving resources (meeting rooms, halls, equipment): browse
resources, create and cancel bookings with overlap validation at the application
level and integrity guarantees at the database level.

## Tech stack

- **Python 3.12**, **Django 6**, **Django REST Framework**
- **PostgreSQL 16** in Docker
- Token authentication (`rest_framework.authtoken`)
- Tests: **pytest-django**, coverage via **coverage** (100%)

## Features

- Resources: list active ones, retrieve a single one by `slug`.
- Bookings: a user sees only their own; can filter by resource.
- Booking creation with validation: end after start, not in the past, no overlap
  with active bookings of the same resource.
- Soft cancellation (`status → cancelled`) — history is kept, the slot is freed.
- Database-level constraints: `CheckConstraint` (end > start) and a partial
  `UniqueConstraint` (one active slot per resource + start time).
- Object-level permissions: only the owner can cancel their booking.

## Requirements

- Python 3.12+
- Docker Desktop (for PostgreSQL)

## Getting started

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd booking-api-project
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Start PostgreSQL in Docker

```bash
docker run -d \
  --name booking-db \
  -e POSTGRES_DB=booking \
  -e POSTGRES_USER=booking_user \
  -e POSTGRES_PASSWORD=booking_pass \
  -p 5432:5432 \
  -v booking_pgdata:/var/lib/postgresql/data \
  postgres:16
```

> If port `5432` is already used by a local PostgreSQL, map the container to
> another port (e.g. `-p 5433:5432`) and set the same value in `POSTGRES_PORT`
> in `.env`.
>
> After a reboot, start the existing container with `docker start booking-db`
> (not `docker run` — it is already created).

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in real values:

```bash
cp .env.example .env
```

| Variable | Example | Description |
|---|---|---|
| `POSTGRES_DB` | `booking` | database name |
| `POSTGRES_USER` | `booking_user` | user |
| `POSTGRES_PASSWORD` | `booking_pass` | password |
| `POSTGRES_HOST` | `localhost` | database host |
| `POSTGRES_PORT` | `5432` | port (must match the one published in Docker) |

### 4. Apply migrations and load demo data

```bash
python manage.py migrate
python manage.py loaddata fixtures        # 4 resources, 4 users, 4 bookings
python manage.py createsuperuser          # optional, for the admin site
python manage.py runserver
```

The app runs at `http://127.0.0.1:8000/`, the admin site at `/admin/`.

## API

All paths are prefixed with `/api/`. Booking endpoints require a token in the
`Authorization: Token <key>` header.

| Method | URL | Description | Auth |
|---|---|---|---|
| `GET` | `/api/resources/` | list active resources (paginated) | no |
| `GET` | `/api/resources/{slug}/` | retrieve a resource by slug | no |
| `POST` | `/api/token/` | obtain a token from username and password | no |
| `GET` | `/api/bookings/` | own bookings; filter `?resource=<slug>` | token |
| `POST` | `/api/bookings/` | create a booking | token |
| `POST` | `/api/bookings/{id}/cancel/` | cancel own booking | token |

### Obtain a token

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -d "username=<user>&password=<password>"
# -> {"token": "<key>"}
```

### Create a booking

```bash
curl -X POST http://127.0.0.1:8000/api/bookings/ \
  -H "Authorization: Token <key>" \
  -H "Content-Type: application/json" \
  -d '{"resource": "conferenceroom-1",
       "start_time": "2026-09-01T10:00:00Z",
       "end_time": "2026-09-01T11:00:00Z"}'
```

Responses: `201` — created; `400` — invalid data or slot already taken; `401` —
no token.

### Cancel a booking

```bash
curl -X POST http://127.0.0.1:8000/api/bookings/1/cancel/ \
  -H "Authorization: Token <key>"
# 200 — cancelled; 403 — not your booking; 400 — already cancelled
```

## Tests

```bash
pytest                                    # run the test suite
pytest --cov=. --cov-report=term-missing  # with a coverage report
```

## Application Docker image

```bash
docker build -t booking-api .
```

> Running the image comes in week 2 (Docker Compose): the app container needs
> network access to the database container.

## Project structure

```
config/            Django settings (settings, urls, wsgi/asgi)
bookings/
  models.py        Resource, Booking + DB constraints
  serializers.py   serializers + validation
  views.py         generic views + APIView for cancellation
  permissions.py   IsOwner (object-level)
  urls.py          /api/ routes
  fixtures/        demo data
  tests/           pytest tests
Dockerfile         application image
```
