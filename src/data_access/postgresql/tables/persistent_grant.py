from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy_utils import ChoiceType

from src.data_access.postgresql.tables.client import Client

from .base import BaseModel

LIFESPAN_OF_TOKEN = 999


class PersistentGrant(BaseModel):
    __tablename__ = "persistent_grants"

    TYPES_OF_GRANTS = [
        ("code", "code"),
        ("refresh_token", "refresh_token"),
        ("urn:ietf:params:oauth:grant-type:device_code", "urn:ietf:params:oauth:grant-type:device_code")
        ]

    key = Column(String(512), unique=True, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))
    data = Column(String(2048), nullable=False)
    expiration = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    type = Column(ChoiceType(TYPES_OF_GRANTS), nullable=False)

    def __str__(self) -> str:
        return f"{self.__tablename__}: {self.key}"
