from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text

from app.database import Base
from app.database import engine

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


with engine.connect() as conn:
    result = conn.execute(
        text("SELECT current_database()")
    )
    print(
        "DATABASE:",
        result.scalar()
    )


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


# ---------------------------
# Database
# ---------------------------
Base.metadata.create_all(
    bind=engine
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