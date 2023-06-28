from typing import Optional, Dict

from sqlalchemy import insert, select, delete
from sqlalchemy.exc import NoResultFound, MultipleResultsFound

from src.data_access.postgresql.repositories.base import BaseRepository
from src.data_access.postgresql.tables.code_challenge import CodeChallenge, CodeChallengeMethod


class CodeChallengeRepository(BaseRepository):
    """Handles operations on Code Challenge data in the database.

    Attributes:
        session: A SQLAlchemy session for database operations.
    """

    async def create(self, client_id: str, code_challenge_method: str, code_challenge: str) -> None:
        """Creates a new code challenge in the database.

        Args:
            client_id: The client ID associated with the code challenge.
            code_challenge_method: The method used to generate the code challenge.
            code_challenge: The code challenge string itself.
        """
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
        """Deletes a code challenge from the database.

        Args:
            client_id: The client ID associated with the code challenge.
        """
        await self.session.execute(
            delete(CodeChallenge).where(CodeChallenge.client_id == client_id)
        )
        await self.session.commit()

    async def get_code_challenge_by_client_id(self, client_id: str) -> CodeChallenge:
        """Gets a code challenge from the database associated with the provided client ID.

        Args:
            client_id: The client ID associated with the code challenge.

        Returns:
            The CodeChallenge instance associated with the provided client ID.

        Raises:
            NoResultFound: If no code challenge is found with the provided client ID.
            MultipleResultsFound: If multiple code challenges are found with the provided client ID.
        """
        result = await self.session.execute(
            select(CodeChallenge).where(
                CodeChallenge.client_id == client_id,
            )
        )

        code_challenge = result.scalars().one()
        return code_challenge

    async def get_code_challenge_method_id(self, code_challenge_method: str) -> int:
        """Gets the ID of a code challenge method from the database based on the provided method name.

        Args:
            code_challenge_method: The name of the code challenge method.

        Returns:
            The ID of the code challenge method associated with the provided method name.

        Raises:
            ValueError: If no code challenge method is found with the provided method name.
        """
        result = await self.session.execute(
            select(CodeChallengeMethod).where(
                CodeChallengeMethod.method == code_challenge_method,
            )
        )

        method = result.scalars().first()

        if not method:
            raise ValueError("Code Challenge Method not found")

        return method.id
