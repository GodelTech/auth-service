from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class Device(BaseModel):
    __tablename__ = "devices"

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship(
        "Client",
        foreign_keys="Device.client_id",
    )

    device_code = Column(String(80), nullable=False, unique=True)
    user_code = Column(String(10), nullable=False, unique=True)
    verification_uri = Column(String, nullable=False)
    verification_uri_complete = Column(String, nullable=False)
    expires_in = Column(Integer, default=600, nullable=False)
    interval = Column(Integer, default=5, nullable=False)

    def __str__(self) -> str:  # pragma: no cover
        return f"Device: {self.device_code}"
