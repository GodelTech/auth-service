from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, CheckConstraint
from sqlalchemy.orm import relationship
from src.data_access.postgresql.tables.client import Client

from .base import BaseModel, Base

LIFESPAN_OF_TOKEN = 999

TYPES_OF_GRANTS = ["code","refresh_token"]



class PersistentGrant(BaseModel):
    __tablename__ = "persistent_grants"
    
    #key = Column(String(512), unique=True, nullable=False)
    #client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))
    #client = relationship("Client", backref = "grants", foreign_keys = "PersistentGrant.client_id" )
    data = Column(String, nullable=False)
    expiration = Column(Integer, nullable=False)
    #subject_id = Column(Integer, ForeignKey("users.id", ondelete='CASCADE'))
    #client = relationship("User", backref = "grants", foreign_keys = "PersistentGrant.subject_id")

    persistent_grant_type_id = Column(Integer, ForeignKey("persistent_grant_types.id", ondelete='CASCADE'), nullable=False)
    persistent_grant_type = relationship("PersistentGrantTypes",  backref="grants", foreign_keys="PersistentGrant.persistent_grant_type_id")

    def __str__(self) -> str:
        return f"{self.data}"

    
class PersistentGrantTypes(Base):
   
    __tablename__ = "persistent_grant_types"
    id = Column(Integer, primary_key=True)
    type_of_grant = Column(String, nullable=False)
    
    def __str__(self):
        return f"{self.type_of_grant}"