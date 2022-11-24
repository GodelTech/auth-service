from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, JSON, String
from sqlalchemy_utils import ChoiceType

from .base import BaseModel

LIFESPAN_OF_TOKEN = 999

class PersistentGrant(BaseModel): 
    __tablename__ = "persistent_grants"

    TYPES_OF_GRANTS =[
        ()
    ]

    key = Column(String(512), unique=True, nullabe=False)
    data = Column(JSON, nullable=False)
    subject_id = Column(Integer, nullable=False)
    type = Column(ChoiceType(TYPES_OF_GRANTS), nullable=False)


    @property
    def expiration(self) -> datetime:
        return datetime(self.created_at) + timedelta(seconds=LIFESPAN_OF_TOKEN)

    def __str__(self) -> str:
        return f"{self.__tablename__}: {self.key}"

