from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, DateTime, Text, PickleType, String
from sqlalchemy.sql import func
from sqlalchemy_utils import ChoiceType

from .base import BaseModel


class PersistentGrants(BaseModel): 
    __tablename__ = "persistent_grants"

    IDS_OF_SUBJECTS = [
        (1, 1),
        (2, 2),
        (3, 3),
        #As many as needed
    ]

    TYPES_OF_GRANTS =[
        ()
    ]

    key = Column(String(512), unique=True, nullabe=False)
    creation_time = Column(DateTime(timezone=True), server_default=func.now())
    data = Column(PickleType, nullable=False)
    subject_id = Column(ChoiceType(IDS_OF_SUBJECTS), nullable=False)
    type = Column(ChoiceType(TYPES_OF_GRANTS), nullable=False)


    @property
    def expiration(self) -> datetime:
        return datetime(self.creation_time) + timedelta(seconds=999)

    def __str__(self) -> str:
        return self.__tablename__

