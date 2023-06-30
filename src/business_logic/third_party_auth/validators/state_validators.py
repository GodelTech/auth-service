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
    """
    Base class for validating state in third-party authentication.

    This class provides the functionality to validate the state parameter in third-party authentication flows.
    Subclasses can implement custom behavior by overriding the `__call__` method.
    """

    def __init__(self, third_party_oidc_repo: ThirdPartyOIDCRepository):
        """
        Initializes a StateValidatorBase object.

        Args:
            third_party_oidc_repo (ThirdPartyOIDCRepository): The repository for accessing third party providers information.
        """
        self._third_party_oidc_repo = third_party_oidc_repo

    async def __call__(self, state: str) -> None:
        """
        Validate the state parameter.

        This method validates the state parameter by checking if it exists in the third-party OIDC repository.
        If the state already exists or does not match the expected format, an exception is raised.

        Args:
            state (str): The state parameter to be validated.

        Raises:
            ThirdPartyAuthInvalidStateError: If the state already exists or does not match the expected format.
        """
        is_state = await self._third_party_oidc_repo.is_state(state)
        if is_state or len(state.split("!_!")) != StateData.STATE_LENGTH.value:
            raise ThirdPartyAuthInvalidStateError("State already exists.")


class StateValidator(StateValidatorBase):
    """
    State validator for third-party authentication.

    This class extends the base StateValidatorBase class and provides additional functionality to delete the state
    after validating it.

    """

    async def __call__(self, state: str) -> None:
        """
        Validate and delete the state parameter.

        This method validates the state parameter by checking if it exists in the third-party OIDC repository.
        If the state does not exist, an exception is raised.
        After successful validation, the state is deleted from the repository.

        Args:
            state (str): The state parameter to be validated and deleted.

        Raises:
            ThirdPartyAuthInvalidStateError: If the state does not exist.

        """
        is_state = await self._third_party_oidc_repo.is_state(state)
        if not is_state:
            raise ThirdPartyAuthInvalidStateError("State does not exist.")
        await self._third_party_oidc_repo.delete_state(state)
