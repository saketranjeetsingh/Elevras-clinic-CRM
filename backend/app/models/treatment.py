from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey

from app.database import Base


class Treatment(Base):

    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id")
    )

    treatment_name = Column(String, nullable=False)

    cost = Column(Integer)

    status = Column(String)

    notes = Column(String)