from __future__ import annotations

from typing import TYPE_CHECKING

from src.business_logic.third_party_auth.errors import (
    ThirdPartyAuthInvalidStateError,
)
from src.business_logic.third_party_auth.constants import StateData

if TYPE_CHECKING:
    from src.data_access.postgresql.repositories import (
        ThirdPartyOIDCRepository,
    )


class StateValidatorBase:
    def __init__(self, third_party_oidc_repo: ThirdPartyOIDCRepository):
        self._third_party_oidc_repo = third_party_oidc_repo

    async def __call__(self, state: str) -> None:
        is_state = await self._third_party_oidc_repo.is_state(state)
        if is_state or len(state.split("!_!")) != StateData.STATE_LENGTH.value:
            raise ThirdPartyAuthInvalidStateError("State already exists.")


class StateValidator(StateValidatorBase):
    async def __call__(self, state: str) -> None:
        is_state = await self._third_party_oidc_repo.is_state(state)
        if not is_state:
            raise ThirdPartyAuthInvalidStateError("State does not exist.")
        await self._third_party_oidc_repo.delete_state(state)