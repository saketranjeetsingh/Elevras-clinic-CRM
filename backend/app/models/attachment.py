from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import func

from app.database import Base


class PatientAttachment(Base):

    __tablename__ = "patient_attachments"

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    patient_id = Column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    doctor_id = Column(
        Integer,
        ForeignKey("doctor_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    filename = Column(String, nullable=False)

    stored_name = Column(String, nullable=False)

    content_type = Column(String, nullable=False)

    size = Column(BigInteger, nullable=False)

    category = Column(String, nullable=False, default="other")

    notes = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)