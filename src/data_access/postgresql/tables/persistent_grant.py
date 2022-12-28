from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy_utils import ChoiceType

from .base import BaseModel
from src.data_access.postgresql.tables.client import Client

LIFESPAN_OF_TOKEN = 999


class PersistentGrant(BaseModel):
    __tablename__ = "persistent_grants"

    TYPES_OF_GRANTS = [
        ('code', 'code')
    ]

    key = Column(String(512), unique=True, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id"))
    data = Column(String(2048), nullable=False)
    expiration = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey("users.id"))
    type = Column(ChoiceType(TYPES_OF_GRANTS), nullable=False)

    def __str__(self) -> str:
        return f"{self.__tablename__}: {self.key}"

