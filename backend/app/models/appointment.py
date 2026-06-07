from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from app.database import Base


class Appointment(Base):

    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )
    doctor_id = Column(
    Integer,
    ForeignKey("doctors.id")
)

    doctor_name = Column(String)

    appointment_date = Column(String)

    status = Column(String)

    notes = Column(String)