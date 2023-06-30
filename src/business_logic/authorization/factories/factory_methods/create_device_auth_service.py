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
    scope_service,
    **kwargs: Any,
) -> AuthServiceProtocol:
    return DeviceAuthService(
        client_validator=ClientValidator(client_repo),
        redirect_uri_validator=RedirectUriValidator(client_repo),
        scope_validator=ScopeValidator(
            client_repo=client_repo,
            scope_service=scope_service
        ),
        user_credentials_validator=UserCredentialsValidator(
            user_repo=user_repo,
            password_service=password_service,
        ),
        user_code_validator=UserCodeValidator(device_repo),
        persistent_grant_repo=persistent_grant_repo,
        device_repo=device_repo,
        user_repo=user_repo,
    )
