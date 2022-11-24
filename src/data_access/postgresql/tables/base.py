import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=datetime.datetime.now)
    updated_at = Column(DateTime, server_default=datetime.datetime.now)
