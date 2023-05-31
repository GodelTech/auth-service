from typing import Optional, Dict

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.code_challenge import CodeChallenge, CodeChallengeMethod


class CodeChallengeRepository(BaseRepository):
    async def create(self, client_id: str, code_challenge_method: str, code_challenge: str) -> None:
        code_challenge_method_id = await self.get_code_challenge_method_id(code_challenge_method)

        code_challenge_data = {
            "client_id": client_id,
            "code_challenge": code_challenge,
            "code_challenge_method_id": code_challenge_method_id,
        }

        await self.session.execute(
            insert(CodeChallenge).values(**code_challenge_data)
        )

        await self.session.commit()

    async def delete_code_challenge_by_client_id(self, client_id: str) -> None:
        await self.session.execute(
            delete(CodeChallenge).where(CodeChallenge.client_id == client_id)
        )
        await self.session.commit()

    async def get_code_challenge_by_client_id(self, client_id: str) -> CodeChallenge:
        result = await self.session.execute(
            select(CodeChallenge).where(
                CodeChallenge.client_id == client_id,
            )
        )

        code_challenge = result.scalars().one()
        return code_challenge

    async def get_code_challenge_method_id(self, code_challenge_method: str) -> int:
        result = await self.session.execute(
            select(CodeChallengeMethod).where(
                CodeChallengeMethod.method == code_challenge_method,
            )
        )

        method = result.scalars().first()

        if not method:
            raise ValueError("Code Challenge Method not found")

        return method.id
