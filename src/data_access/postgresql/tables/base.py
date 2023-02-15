import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, server_default=func.now(), onupdate=datetime.datetime.utcnow, default=datetime.datetime.utcnow
    )
