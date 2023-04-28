from httpx import AsyncClient

from src.business_logic.services import (
    AdminAuthService,
    AdminGroupService,
    AdminRoleService,
    AdminUserService,
    AuthorizationService,
    AuthThirdPartyOIDCService,
    ThirdPartyGoogleService,
    ThirdPartyFacebookService,
    ThirdPartyLinkedinService,
    ThirdPartyGitLabService,
    ThirdPartyMicrosoftService,
    DeviceService,
    EndSessionService,
    IntrospectionServies,
    JWTService,
    LoginFormService,
    PasswordHash,
    ThirdPartyFacebookService,
    ThirdPartyGitLabService,
    ThirdPartyGoogleService,
    ThirdPartyLinkedinService,
    TokenService,
    UserInfoServices,
    WellKnownServices,
)
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    GroupRepository,
    PersistentGrantRepository,
    RoleRepository,
    ThirdPartyOIDCRepository,
    UserRepository,
    WellKnownRepository,
    BlacklistedTokenRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession


def provide_auth_service_stub() -> None:  # pragma: no cover
    ...


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


def provide_password_service_stub() -> None:  # pragma: no cover
    ...


def provide_password_service() -> PasswordHash:
    return PasswordHash()


def provide_endsession_service_stub() -> None:  # pragma: no cover
    ...


def provide_endsession_service(
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
    jwt_service: JWTService,
) -> EndSessionService:
    return EndSessionService(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        jwt_service=jwt_service,
    )


def provide_jwt_service_stub() -> None:  # pragma: no cover
    ...


def provide_jwt_service() -> JWTService:
    return JWTService()


def provide_introspection_service_stub() -> None:  # pragma: no cover
    ...


def provide_introspection_service(
    jwt: JWTService,
    # token_service: TokenService,
    user_repo: UserRepository,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
) -> IntrospectionServies:
    return IntrospectionServies(
        jwt=jwt,
        # token_service=token_service,
        user_repo=user_repo,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
    )


def provide_token_service_stub() -> None:  # pragma: no cover
    ...


def provide_token_service(
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
    user_repo: UserRepository,
    device_repo: DeviceRepository,
    jwt_service: JWTService,
    blacklisted_repo: BlacklistedTokenRepository,
) -> TokenService:
    return TokenService(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
        device_repo=device_repo,
        jwt_service=jwt_service,
        blacklisted_repo=blacklisted_repo,
    )


def provide_admin_user_service_stub() -> None:  # pragma: no cover
    ...


def provide_admin_user_service(
    user_repo: UserRepository,
    role_repo: RoleRepository,
    session:AsyncSession
) -> AdminUserService:
    return AdminUserService(
        user_repo=user_repo,
        role_repo=role_repo,
        session=session
    )


def provide_admin_group_service_stub() -> None:  # pragma: no cover
    ...


def provide_admin_group_service(
    session: AsyncSession,
) -> AdminGroupService:
    return AdminGroupService(
        session=session,
    )


def provide_admin_role_service_stub() -> None:  # pragma: no cover
    ...


def provide_admin_role_service(
    role_repo: RoleRepository,
) -> AdminRoleService:
    return AdminRoleService(
        role_repo=role_repo,
    )


def provide_wellknown_service_stub() -> None:
    ...


def provide_wellknown_service(
    wlk_repo: WellKnownRepository,
) -> WellKnownServices:
    return WellKnownServices(
        wlk_repo=wlk_repo,
    )


def provide_userinfo_service_stub() -> None:  # pragma: no cover
    ...


def provide_userinfo_service(
    jwt: JWTService,
    # token_service: TokenService,
    user_repo: UserRepository,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
) -> UserInfoServices:
    return UserInfoServices(
        jwt=jwt,
        # token_service=token_service,
        user_repo=user_repo,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
    )


def provide_login_form_service_stub() -> None:  # pragma: no cover
    ...


def provide_login_form_service(
    client_repo: ClientRepository,
    oidc_repo: ThirdPartyOIDCRepository,
) -> LoginFormService:
    return LoginFormService(client_repo=client_repo, oidc_repo=oidc_repo)


def provide_admin_auth_service_stub() -> None:  # pragma: no cover
    ...


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


def provide_device_service_stub() -> None:  # pragma: no cover
    ...


def provide_device_service(
    client_repo: ClientRepository,
    device_repo: DeviceRepository,
) -> DeviceService:
    return DeviceService(client_repo=client_repo, device_repo=device_repo)


def provide_auth_third_party_oidc_service_stub() -> None:  # pragma: no cover
    ...


def provide_auth_third_party_oidc_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> AuthThirdPartyOIDCService:
    return AuthThirdPartyOIDCService(
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_auth_third_party_linkedin_service_stub() -> (
    None
):  # pragma: no cover
    ...


def provide_auth_third_party_linkedin_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyLinkedinService:
    return ThirdPartyLinkedinService(
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_third_party_google_service_stub() -> None:  # pragma: no cover
    ...


def provide_third_party_google_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyGoogleService:
    return ThirdPartyGoogleService(
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_third_party_facebook_service_stub() -> None:  # pragma: no cover
    ...


def provide_third_party_facebook_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyFacebookService:
    return ThirdPartyFacebookService(
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_third_party_gitlab_service_stub() -> None:  # pragma: no cover
    ...


def provide_third_party_gitlab_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyGitLabService:
    return ThirdPartyGitLabService(
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )


def provide_third_party_microsoft_service_stub() -> None:  # pragma: no cover
    ...


def provide_third_party_microsoft_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    oidc_repo: ThirdPartyOIDCRepository,
    persistent_grant_repo: PersistentGrantRepository,
    http_client: AsyncClient,
) -> ThirdPartyMicrosoftService:
    return ThirdPartyMicrosoftService(
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        oidc_repo=oidc_repo,
        http_client=http_client,
    )
