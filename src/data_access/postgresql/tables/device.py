from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


from .base import BaseModel


class Device(BaseModel):
    __tablename__ = "devices"

    client_id = Column(String(80), ForeignKey("clients.client_id", ondelete='CASCADE'))
    device_code = Column(String(80), nullable=False, unique=True)
    user_code = Column(String(10), nullable=False, unique=True)
    verification_uri = Column(String, nullable=False)
    verification_uri_complete = Column(String, nullable=False)
    expires_in = Column(Integer, default=600, nullable=False)
    interval = Column(Integer, default=5, nullable=False)

    