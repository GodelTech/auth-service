from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class CodeChallenge(BaseModel):
    __tablename__ = "code_challenges"

    client_id = Column(Integer, ForeignKey("clients.id", ondelete="CASCADE"))
    client = relationship(
        "Client",
        back_populates='code_challenges',
        lazy='immediate'
    )
    code_challenge = Column(String, nullable=False)
    code_challenge_method_id = Column(
        Integer,
        ForeignKey("code_challenge_methods.id", ondelete="CASCADE"),
        nullable=False,
    )
    code_challenge_method = relationship(
        "CodeChallengeMethod",
        backref="code_challenges",
        lazy='joined'
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"CodeChallenge: {self.code_challenge} ({self.code_challenge_method}) for client {self.client_id}"


class CodeChallengeMethod(BaseModel):
    __tablename__ = "code_challenge_methods"
    method = Column(String, nullable=False)
    code_challenges = relationship(
        "CodeChallenge",
        backref="code_challenge_methods",
        lazy='noload',
    )

    def __str__(self) -> str:  # pragma: no cover
        return f"CodeChallengeMethod: {self.method}"
