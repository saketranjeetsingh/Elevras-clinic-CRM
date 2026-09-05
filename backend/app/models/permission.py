from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import func

from app.database import Base


class Permission(Base):

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)

    code = Column(String, unique=True, nullable=False, index=True)

    description = Column(String)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)