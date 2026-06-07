from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from app.database import Base


class Bill(Base):

    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )
    doctor_id = Column(
    Integer,
    ForeignKey("doctors.id")
)

    amount = Column(Integer)

    payment_status = Column(String)

    payment_method = Column(String)