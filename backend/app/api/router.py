from fastapi import APIRouter

from app.api.routes import auth, users, doctors, reservations

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(doctors.router)
api_router.include_router(reservations.router)
