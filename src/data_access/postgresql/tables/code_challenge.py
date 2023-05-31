from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import BaseModel


class CodeChallenge(BaseModel):
    __tablename__ = "code_challenges"

    client_id = Column(String, ForeignKey("clients.client_id", ondelete="CASCADE"))
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

    def __str__(self) -> str:  # pragma: no cover
        return f"CodeChallengeMethod: {self.method}"
