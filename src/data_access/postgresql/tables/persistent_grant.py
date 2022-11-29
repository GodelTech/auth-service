from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, JSON, String, DateTime
from sqlalchemy_utils import ChoiceType

from .base import BaseModel

LIFESPAN_OF_TOKEN = 999


class PersistentGrant(BaseModel): 
    __tablename__ = "persistent_grants"

    TYPES_OF_GRANTS = [
        ('example', 'Example')
    ]

    key = Column(String(512), unique=True, nullable=False)
    data = Column(JSON, nullable=False)
    expiration = Column(DateTime, nullable=False)
    subject_id = Column(Integer, nullable=False)
    type = Column(ChoiceType(TYPES_OF_GRANTS), nullable=False)

    def __str__(self) -> str:
        return f"{self.__tablename__}: {self.key}"

