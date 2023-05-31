from __future__ import annotations

from typing import TYPE_CHECKING, Any

from src.business_logic.authorization.service_impls import DeviceAuthService
from src.business_logic.authorization.validators import (
    ScopeValidator,
    UserCodeValidator,
    UserCredentialsValidator,
)
from src.business_logic.common.validators import (
    ClientValidator,
    RedirectUriValidator,
)

if TYPE_CHECKING:
    from src.business_logic.authorization.interfaces import AuthServiceProtocol
    from src.business_logic.services import PasswordHash
    from src.data_access.postgresql.repositories import (
        ClientRepository,
        DeviceRepository,
        PersistentGrantRepository,
        UserRepository,
    )


def _create_device_auth_service(
    *,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    persistent_grant_repo: PersistentGrantRepository,
    device_repo: DeviceRepository,
    password_service: PasswordHash,
    **kwargs: Any,
) -> AuthServiceProtocol:
    """
    Factory method for creating an instance of DeviceAuthService.

    Args:
        client_repo: The repository for accessing client-related data.
        user_repo: The repository for accessing user-related data.
        persistent_grant_repo: The repository for accessing persistent grant-related data.
        device_repo: The repository for accessing device-related data.
        password_service: The service for password hashing and verification.
        **kwargs: Additional keyword arguments.

    Returns:
        An instance of DeviceAuthService.

    """
    return DeviceAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(client_repo),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
        user_code_validator=UserCodeValidator(device_repo),
        persistent_grant_repo=persistent_grant_repo,
        device_repo=device_repo,
        user_repo=user_repo,
    )
