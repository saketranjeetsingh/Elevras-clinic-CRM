from contextlib import asynccontextmanager

import os
import time

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy import text

from app.database import Base
from app.database import engine
import logging

# Models - imported to register with Base.metadata
from app.models import (
    patient,
    appointment,
    treatment,
    bill,
    doctor,
    attachment,
    organization,
    user,
    role,
    permission,
    user_role,
    role_permission,
    doctor_profile,
    audit_log,
    refresh_token,
)

# Routers
from app.routers.patients import router as patient_router
from app.routers.appointments import router as appointment_router
from app.routers.treatments import router as treatment_router
from app.routers.bills import router as bill_router
from app.routers.dashboard import router as dashboard_router
from app.routers.auth import router as auth_router
from app.routers.attachments import router as attachment_router
from app.routers.organizations import router as organization_router
from app.routers.users import router as user_router
from app.routers.roles import router as role_router


# Load environment variables from backend/.env (if present)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Connect to PostgreSQL.
    Tables are managed via Alembic migrations.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            logger.info("DATABASE: %s", result.scalar())

        # For fresh dev DBs, create tables if they don't exist
        # In production, use `alembic upgrade head` instead
        # Set AUTO_CREATE_TABLES=true to enable (dev only)
        if os.environ.get("AUTO_CREATE_TABLES", "false").lower() == "true":
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created (AUTO_CREATE_TABLES=true)")

    except Exception as exc:
        raise RuntimeError(
            "Could not connect to Postgres — check DATABASE_URL and that Postgres is running. "
            f"Original error: {exc}"
        )

    yield


app = FastAPI(lifespan=lifespan)


# ----------------------------
# Request logging
# ----------------------------
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# ----------------------------
# CORS
# ----------------------------
cors_origins_env = os.environ.get("CORS_ORIGINS", "http://localhost:5173")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# Routers
# ----------------------------
app.include_router(auth_router)
app.include_router(organization_router)
app.include_router(user_router)
app.include_router(role_router)
app.include_router(patient_router)
app.include_router(appointment_router)
app.include_router(treatment_router)
app.include_router(bill_router)
app.include_router(dashboard_router)
app.include_router(attachment_router)


@app.get("/")
def home():
    return {
        "message": "Elevras API Running"
    }


@app.get("/health")
def health():
    database_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        database_ok = False

    return JSONResponse(
        status_code=200 if database_ok else 503,
        content={
            "status": "ok" if database_ok else "degraded",
            "database": "ok" if database_ok else "error",
        },
    )