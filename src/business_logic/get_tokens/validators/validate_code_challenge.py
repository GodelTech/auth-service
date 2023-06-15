from __future__ import annotations

import base64
import hashlib
from typing import TYPE_CHECKING
from sqlalchemy.exc import NoResultFound
from cryptography.fernet import Fernet

from src.config.settings.app import AppSettings
from src.business_logic.get_tokens.errors import InvalidPkceCodeError

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import CodeChallengeRepository


class ValidatePKCECode:
    def __init__(
            self, 
            code_challenge_repo: CodeChallengeRepository
    ) -> None:
        self._code_challenge_repo = code_challenge_repo

    async def __call__(self, client_id: str, code_verifier: str) -> None:
        try:
            code_challenge = await self._code_challenge_repo.get_code_challenge_by_client_id(
                client_id=client_id
            )
            code_challenge_method = code_challenge.code_challenge_method.method
            code_challenge = code_challenge.code_challenge
        except NoResultFound:
            code_challenge = None
            code_challenge_method = None
        
        if code_challenge:
            if code_challenge_method == "plain":
                if code_verifier != code_challenge:
                    raise InvalidPkceCodeError
            elif code_challenge_method == "S256":
                fernet = Fernet(AppSettings().secret_key.get_secret_value())
                expected_code_challenge = fernet.decrypt(
                    code_challenge.encode()
                ).decode()
                actual_code_challenge = base64.urlsafe_b64encode(
                    hashlib.sha256(code_verifier.encode("utf-8")).digest()
                ).decode().rstrip("=")
                if expected_code_challenge != actual_code_challenge:
                    raise InvalidPkceCodeError
            
            await self._code_challenge_repo.delete_code_challenge_by_client_id(client_id=client_id)
