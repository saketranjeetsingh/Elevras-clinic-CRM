from contextlib import asynccontextmanager

import os
import time

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sqlalchemy import text
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base
from app.database import engine
import logging

# Models
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.treatment import Treatment
from app.models.bill import Bill
from app.models.doctor import Doctor
from app.models.attachment import PatientAttachment

# Routers
from app.routers.patients import router as patient_router
from app.routers.appointments import router as appointment_router
from app.routers.treatments import router as treatment_router
from app.routers.bills import router as bill_router
from app.routers.dashboard import router as dashboard_router
from app.routers.auth import router as auth_router
from app.routers.attachments import router as attachment_router


# Load environment variables from backend/.env (if present)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

logger = logging.getLogger("uvicorn.error")


def ensure_schema():
    """Update existing databases safely without affecting fresh installs."""
    with engine.begin() as conn:
        inspector = inspect(conn)
        existing_tables = set(inspector.get_table_names())

        # Add doctor_id column if missing
        for table_name, column_name in [
            ("patients", "doctor_id"),
            ("appointments", "doctor_id"),
            ("treatments", "doctor_id"),
            ("bills", "doctor_id"),
        ]:
            if table_name not in existing_tables:
                continue

            columns = {col["name"] for col in inspector.get_columns(table_name)}

            if column_name not in columns:
                conn.execute(
                    text(
                        f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} INTEGER"
                    )
                )

        # Add common data-integrity columns if missing
        for table_name, columns in {
            "doctors": ["created_at", "updated_at"],
            "patients": ["created_at", "updated_at", "blood_group", "medical_history"],
            "appointments": ["created_at", "updated_at"],
            "treatments": ["created_at", "updated_at", "treatment_date"],
            "bills": ["created_at", "updated_at"],
        }.items():
            if table_name not in existing_tables:
                continue

            existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
            for column_name in columns:
                if column_name not in existing_columns:
                    sql_type = "TIMESTAMP WITH TIME ZONE" if "at" in column_name else "TEXT"
                    if column_name == "treatment_date":
                        sql_type = "TIMESTAMP WITH TIME ZONE"
                    conn.execute(
                        text(
                            f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} {sql_type}"
                        )
                    )

        # Add patient profile columns if missing
        if "patients" in existing_tables:
            patient_columns = {col["name"] for col in inspector.get_columns("patients")}
            for column_name in ["blood_group", "medical_history"]:
                if column_name not in patient_columns:
                    conn.execute(
                        text(
                            f"ALTER TABLE patients ADD COLUMN IF NOT EXISTS {column_name} TEXT"
                        )
                    )

        # Preserve orphaned data safely instead of silently assigning it to doctor 1.
        for table_name in ["patients", "appointments", "treatments", "bills"]:
            if table_name not in existing_tables:
                continue

            null_count = conn.execute(
                text(f"SELECT COUNT(*) FROM {table_name} WHERE doctor_id IS NULL")
            ).scalar()

            if null_count:
                logger.warning(
                    "Found %s rows in %s with NULL doctor_id; leaving them untouched to preserve multi-doctor isolation.",
                    null_count,
                    table_name,
                )

        # Patient unique constraints
        if "patients" in existing_tables:
            unique_constraints = inspector.get_unique_constraints("patients")
            constraint_names = {c["name"] for c in unique_constraints}

            for constraint in unique_constraints:
                column_names = constraint.get("column_names", [])

                if column_names in (["phone"], ["email"]):
                    if constraint["name"] in constraint_names:
                        conn.execute(
                            text(
                                f'ALTER TABLE patients DROP CONSTRAINT IF EXISTS "{constraint["name"]}"'
                            )
                        )

            new_constraints = [
                ("uq_patient_doctor_phone", ["doctor_id", "phone"]),
                ("uq_patient_doctor_email", ["doctor_id", "email"]),
            ]

            for constraint_name, columns in new_constraints:
                existing_constraint = next(
                    (
                        c
                        for c in inspector.get_unique_constraints("patients")
                        if c.get("column_names") == columns
                    ),
                    None,
                )

                if existing_constraint is None:
                    try:
                        conn.execute(
                            text(
                                f'ALTER TABLE patients ADD CONSTRAINT "{constraint_name}" UNIQUE ({", ".join(columns)})'
                            )
                        )
                    except SQLAlchemyError:
                        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Connect to PostgreSQL,
    create tables if they don't exist,
    then run schema migrations for older databases.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            logger.info("DATABASE: %s", result.scalar())

        # IMPORTANT:
        # Create tables FIRST
        Base.metadata.create_all(bind=engine)

        # Then update existing databases
        ensure_schema()

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