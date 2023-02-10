import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=datetime.datetime.now
    )


class Note(BaseModel):
    __tablename__ = "notes"

    title = Column(String, nullable=False, index=True)
    content = Column(String, index=True)
    user_id = Column(
        Integer,
    )  # ForeignKey("xyz"))
    # user = relationship("xyz")
