from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, CheckConstraint
from src.data_access.postgresql.tables.client import Client

from .base import BaseModel

LIFESPAN_OF_TOKEN = 999

TYPES_OF_GRANTS = ["code","refresh_token"]

class PersistentGrant(BaseModel):
    __tablename__ = "persistent_grants"
    __table_args__ =  (
                    CheckConstraint(
                    sqltext= f'"type" IN {str(TYPES_OF_GRANTS)[1:-1]}', 
                    name = "type_in_list"
                    ),)
    
    key = Column(String(512), unique=True, nullable=False)
    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))
    data = Column(String(2048), nullable=False)
    expiration = Column(Integer, nullable=False)
    subject_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    type = Column(String(29), nullable=False)

    def __str__(self) -> str:
        return f"{self.__tablename__}: {self.key}"
