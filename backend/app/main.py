from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy import inspect

from app.database import Base
from app.database import engine
import logging

# Models
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.treatment import Treatment
from app.models.bill import Bill
from app.models.doctor import Doctor

# Routers
from app.routers.patients import router as patient_router
from app.routers.appointments import router as appointment_router
from app.routers.treatments import router as treatment_router
from app.routers.bills import router as bill_router
from app.routers.dashboard import router as dashboard_router
from app.routers.auth import router as auth_router


logger = logging.getLogger("uvicorn.error")


def ensure_schema():
    """Add missing columns to existing tables without dropping data."""
    with engine.begin() as conn:
        inspector = inspect(conn)
        existing_tables = set(inspector.get_table_names())

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
                conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS {column_name} INTEGER"))

        conn.execute(text("UPDATE patients SET doctor_id = 1 WHERE doctor_id IS NULL"))
        conn.execute(text("UPDATE appointments SET doctor_id = 1 WHERE doctor_id IS NULL"))
        conn.execute(text("UPDATE treatments SET doctor_id = 1 WHERE doctor_id IS NULL"))
        conn.execute(text("UPDATE bills SET doctor_id = 1 WHERE doctor_id IS NULL"))


app = FastAPI()


# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Attempt a DB connection at startup and create tables.

    If the connection fails, raise a clear RuntimeError so the developer
    sees an informative message (e.g. bad DATABASE_URL or Postgres not running).
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT current_database()"))
            logger.info("DATABASE: %s", result.scalar())

        ensure_schema()

        # Create tables after successful connection
        Base.metadata.create_all(bind=engine)

    except Exception as exc:
        # Provide a readable error message to help local development debugging
        raise RuntimeError(
            "Could not connect to Postgres — check DATABASE_URL and that Postgres is running. "
            f"Original error: {exc}"
        )


# ---------------------------
# Routers
# ---------------------------
app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(appointment_router)
app.include_router(treatment_router)
app.include_router(bill_router)
app.include_router(dashboard_router)


@app.get("/")
def home():

    return {
        "message": "Elevras API Running"
    }