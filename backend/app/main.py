from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

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


app = FastAPI()


# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
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