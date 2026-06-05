from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from app.database import Base


class Patient(Base):

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    phone = Column(String, unique=True, nullable=False)

    email = Column(String, unique=True)

    age = Column(Integer)

    gender = Column(String)

    notes = Column(String)

    last_treatment = Column(String)