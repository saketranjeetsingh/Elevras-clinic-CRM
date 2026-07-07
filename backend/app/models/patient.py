from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint

from app.database import Base


class Patient(Base):

    __tablename__ = "patients"
    __table_args__ = (
        UniqueConstraint("doctor_id", "phone", name="uq_patient_doctor_phone"),
        UniqueConstraint("doctor_id", "email", name="uq_patient_doctor_email"),
    )

    id = Column(Integer, primary_key=True, index=True)

    doctor_id = Column(
        Integer,
        ForeignKey("doctors.id")
    )

    name = Column(String, nullable=False)

    phone = Column(String, nullable=False)

    email = Column(String)

    age = Column(Integer)

    gender = Column(String)

    notes = Column(String)

    last_treatment = Column(String)