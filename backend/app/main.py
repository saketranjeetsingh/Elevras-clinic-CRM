from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Routers
from app.routers.patients import router as patient_router
from app.routers.appointments import router as appointment_router
from app.routers.treatments import router as treatment_router
from app.routers.bills import router as bill_router
from app.routers.dashboard import router as dashboard_router
from app.routers.auth import router as auth_router


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

        # Add patient profile columns if missing
        if "patients" in existing_tables:
            patient_columns = {col["name"] for col in inspector.get_columns("patients")}
            for column_name in ["address", "blood_group", "medical_history"]:
                if column_name not in patient_columns:
                    conn.execute(
                        text(
                            f"ALTER TABLE patients ADD COLUMN IF NOT EXISTS {column_name} TEXT"
                        )
                    )

        # Update existing rows only if the table exists
        for table in ["patients", "appointments", "treatments", "bills"]:
            if table in existing_tables:
                conn.execute(
                    text(f"UPDATE {table} SET doctor_id = 1 WHERE doctor_id IS NULL")
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


app = FastAPI()


# ----------------------------
# CORS
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
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


# ----------------------------
# Routers
# ----------------------------
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