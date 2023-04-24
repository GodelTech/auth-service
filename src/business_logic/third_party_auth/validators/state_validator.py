from __future__ import annotations

from typing import TYPE_CHECKING

from src.data_access.postgresql.errors import ThirdPartyStateNotFoundError

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import (
        ThirdPartyOIDCRepository,
    )


class StateValidator:
    def __init__(self, third_party_oidc_repo: ThirdPartyOIDCRepository):
        self._third_party_oidc_repo = third_party_oidc_repo

    async def __call__(self, state: str) -> None:
        is_state = await self._third_party_oidc_repo.is_state(state)
        if not is_state:
            raise ThirdPartyStateNotFoundError("State does not exist.")
        await self._third_party_oidc_repo.delete_state(state)
