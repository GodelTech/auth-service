from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from src.business_logic.services.admin_auth import AdminAuthService
from src.business_logic.services.admin_api import (
    AdminGroupService,
    AdminRoleService,
    AdminUserService,
)
from src.business_logic.services.authorization.authorization_service import (
    AuthorizationService,
)
from src.business_logic.services.third_party_oidc_service import (
    AuthThirdPartyOIDCService,
)
from src.business_logic.services.device_auth import DeviceService
from src.business_logic.services.endsession import EndSessionService
from src.business_logic.services.introspection import IntrospectionService
from src.business_logic.services.jwt_token import JWTService
from src.business_logic.services.login_form_service import LoginFormService
from src.business_logic.services.password import PasswordHash
from src.business_logic.services.third_party_oidc_service import (
    ThirdPartyFacebookService,
    ThirdPartyGitLabService,
    ThirdPartyGoogleService,
    ThirdPartyLinkedinService,
    ThirdPartyMicrosoftService,
)
from src.business_logic.services.tokens import TokenService
from src.business_logic.services.userinfo import UserInfoServices
from src.business_logic.services.well_known import WellKnownServices
from src.business_logic.services.client import ClientService


from src.data_access.postgresql.repositories import (
    BlacklistedTokenRepository,
    ClientRepository,
    DeviceRepository,
    GroupRepository,
    PersistentGrantRepository,
    RoleRepository,
    ThirdPartyOIDCRepository,
    UserRepository,
    WellKnownRepository,
    CodeChallengeRepository,
)


def provide_auth_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    persistent_grant_repo: PersistentGrantRepository,
    device_repo: DeviceRepository,
    password_service: PasswordHash,
    jwt_service: JWTService,
) -> AuthorizationService:
    return AuthorizationService(
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        device_repo=device_repo,
        password_service=password_service,
        jwt_service=jwt_service,
    )


def provide_password_service() -> PasswordHash:
    return PasswordHash()


def provide_endsession_service(
    session: AsyncSession,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
    jwt_service: JWTService,
) -> EndSessionService:
    return EndSessionService(
        session=session,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        jwt_service=jwt_service,
    )


def provide_jwt_service() -> JWTService:
    return JWTService()


def provide_introspection_service(
    session: AsyncSession,
    jwt: JWTService,
    user_repo: UserRepository,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
) -> IntrospectionService:
    return IntrospectionService(
        jwt=jwt,
        user_repo=user_repo,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
    )


def provide_token_service(
    session: AsyncSession,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
    user_repo: UserRepository,
    device_repo: DeviceRepository,
    code_challenge_repo: CodeChallengeRepository,
    jwt_service: JWTService,
    blacklisted_repo: BlacklistedTokenRepository,
) -> TokenService:
    return TokenService(
        session=session,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
        device_repo=device_repo,
        code_challenge_repo=code_challenge_repo,
        jwt_service=jwt_service,
        blacklisted_repo=blacklisted_repo,
    )


def provide_admin_user_service(
    user_repo: UserRepository, role_repo: RoleRepository, session: AsyncSession
) -> AdminUserService:
    return AdminUserService(
        user_repo=user_repo, role_repo=role_repo, session=session
    )


def provide_admin_group_service(
    session: AsyncSession, group_repo: GroupRepository
) -> AdminGroupService:
    return AdminGroupService(session=session, group_repo=group_repo)


def provide_admin_role_service(
    session: AsyncSession,
    role_repo: RoleRepository,
) -> AdminRoleService:
    return AdminRoleService(
        session=session,
        role_repo=role_repo,
    )


def provide_wellknown_service(
    session: AsyncSession,
    wlk_repo: WellKnownRepository,
) -> WellKnownServices:
    return WellKnownServices(
        session=session,
        wlk_repo=wlk_repo,
    )


def provide_userinfo_service(
    session: AsyncSession,
    jwt: JWTService,
    user_repo: UserRepository,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
) -> UserInfoServices:
    return UserInfoServices(
        session=session,
        jwt=jwt,
        user_repo=user_repo,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
    )


def provide_login_form_service(
    client_repo: ClientRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    session: AsyncSession,
) -> LoginFormService:
    return LoginFormService(
        client_repo=client_repo, oidc_repo=oidc_repo, session=session
    )


def provide_admin_auth_service(
    user_repo: UserRepository,
    password_service: PasswordHash,
    jwt_service: JWTService,
) -> AdminAuthService:
    return AdminAuthService(
        user_repo=user_repo,
        password_service=password_service,
        jwt_service=jwt_service,
    )


def provide_device_service(
    client_repo: ClientRepository,
    device_repo: DeviceRepository,
    session: AsyncSession,
) -> DeviceService:
    return DeviceService(
        session=session, client_repo=client_repo, device_repo=device_repo
    )


def provide_auth_third_party_oidc_service(
    session: AsyncSession,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> AuthThirdPartyOIDCService:
    return AuthThirdPartyOIDCService(
        session=session,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_auth_third_party_linkedin_service(
    session: AsyncSession,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyLinkedinService:
    return ThirdPartyLinkedinService(
        session=session,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_third_party_google_service(
    session: AsyncSession,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyGoogleService:
    return ThirdPartyGoogleService(
        session=session,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_third_party_facebook_service(
    session: AsyncSession,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyFacebookService:
    return ThirdPartyFacebookService(
        session=session,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_third_party_gitlab_service(
    session: AsyncSession,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyGitLabService:
    return ThirdPartyGitLabService(
        session=session,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_third_party_microsoft_service_stub() -> None:  # pragma: no cover
    ...


def provide_third_party_microsoft_service(
    session: AsyncSession,
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyMicrosoftService:
    return ThirdPartyMicrosoftService(
        session=session,
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_client_service(
    client_repo: ClientRepository,
) -> ClientService:
    return ClientService(
        client_repo=client_repo,
    )
