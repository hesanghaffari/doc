# Clinic Booking System — Backend

## Local development

1. Copy the environment file:
   ```
   cp backend/.env.example backend/.env
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
backend/
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
docker-compose.yml -> local dev: backend + Postgres
```

## Roles

- `patient` — registers via `/api/v1/auth/register`, books/cancels appointment slots
- `doctor` — created by an admin, opens up appointment slots for themselves
- `admin` — creates doctor accounts

## Next steps

- Kubernetes manifests (Deployment, Service, Ingress, ConfigMap, Secret, PVC)
- React frontend
- Deployment to Arvan Cloud (Container Registry + Cloud Container)
