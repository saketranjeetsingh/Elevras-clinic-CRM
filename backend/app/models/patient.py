from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import func

from app.database import Base


class Patient(Base):

    __tablename__ = "patients"
    __table_args__ = (
        UniqueConstraint("organization_id", "phone", name="uq_patient_org_phone"),
        UniqueConstraint("organization_id", "email", name="uq_patient_org_email"),
    )

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    name = Column(String, nullable=False)

    phone = Column(String, nullable=False)

    email = Column(String)

    date_of_birth = Column(DateTime(timezone=True), nullable=True)

    gender = Column(String)

    blood_group = Column(String)

    medical_history = Column(String)

    notes = Column(String)

    last_treatment = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )