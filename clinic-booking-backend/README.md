# Clinic Booking System — Backend

FastAPI + PostgreSQL backend for a clinic appointment booking system.
The frontend lives in a separate repository: clinic-booking-frontend.

## Local development

1. Copy the environment file and set a real SECRET_KEY:
   ```
   cp .env.example .env
   ```
2. Start the stack:
   ```
   docker compose up --build
   ```
3. Run the first database migration (once, after containers are up):
   ```
   docker compose exec backend alembic revision --autogenerate -m "initial schema"
   docker compose exec backend alembic upgrade head
   ```
4. API docs available at http://localhost:8000/docs

## Project layout

```
app/
  core/       -> config, database engine, security (JWT + password hashing)
  models/     -> SQLAlchemy ORM models (User, Doctor, AppointmentSlot, Reservation)
  schemas/    -> Pydantic request/response schemas
  api/
    deps.py       -> auth dependency (get_current_user, require_role)
    router.py     -> aggregates all route modules
    routes/       -> auth.py, users.py, doctors.py, reservations.py
  main.py     -> FastAPI app entrypoint, CORS, /health for k8s probes
alembic/      -> database migrations
Dockerfile    -> multi-stage build (builder + slim runtime, non-root user)
```

## Roles

- `patient` — registers via `/api/v1/auth/register`, books/cancels appointment slots
- `doctor` — created by an admin, opens up appointment slots for themselves
- `admin` — creates doctor accounts

## CORS

Allowed frontend origins are set via the `CORS_ORIGINS` environment variable
(comma-separated). Defaults to `http://localhost:5173` for local development
against the frontend repo. Update this to your deployed frontend's URL in
production.

## Next steps

- Kubernetes manifests (Deployment, Service, Ingress, ConfigMap, Secret, PVC)
- Deployment to Arvan Cloud (Container Registry + Cloud Container)
