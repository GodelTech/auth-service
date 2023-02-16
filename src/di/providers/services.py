from src.business_logic.services import (
    AdminAuthService,
    AdminGroupService,
    AdminRoleService,
    AdminUserService,
    AuthorizationService,
    DeviceService,
    EndSessionService,
    IntrospectionServies,
    JWTService,
    LoginFormService,
    PasswordHash,
    TokenService,
    UserInfoServices,
)
from src.data_access.postgresql.repositories import (
    ClientRepository,
    DeviceRepository,
    GroupRepository,
    PersistentGrantRepository,
    RoleRepository,
    UserRepository,
)


def provide_auth_service_stub() -> None:
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


def provide_password_service_stub() -> None:
    ...


def provide_password_service() -> PasswordHash:
    return PasswordHash()


def provide_endsession_service_stub() -> None:
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


def provide_jwt_service_stub() -> None:
    ...


def provide_jwt_service() -> JWTService:
    return JWTService()


def provide_introspection_service_stub() -> None:
    ...


def provide_introspection_service(
    jwt: JWTService,
    user_repo: UserRepository,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
) -> IntrospectionServies:
    return IntrospectionServies(
        jwt=jwt,
        user_repo=user_repo,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
    )


def provide_token_service_stub() -> None:
    ...


def provide_token_service(
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
    user_repo: UserRepository,
    device_repo: DeviceRepository,
    jwt_service: JWTService,
) -> TokenService:
    return TokenService(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
        device_repo=device_repo,
        jwt_service=jwt_service,
    )


def provide_admin_user_service_stub() -> None:
    ...


def provide_admin_user_service(
    user_repo: UserRepository,
) -> AdminUserService:
    return AdminUserService(
        user_repo=user_repo,
    )


def provide_admin_group_service_stub() -> None:
    ...


def provide_admin_group_service(
    group_repo: GroupRepository,
) -> AdminGroupService:
    return AdminGroupService(
        group_repo=group_repo,
    )


def provide_admin_role_service_stub() -> None:
    ...


def provide_admin_role_service(
    role_repo: RoleRepository,
) -> AdminRoleService:
    return AdminRoleService(
        role_repo=role_repo,
    )


def provide_userinfo_service_stub() -> None:
    ...


def provide_userinfo_service(
    jwt: JWTService,
    user_repo: UserRepository,
    client_repo: ClientRepository,
    persistent_grant_repo: PersistentGrantRepository,
) -> UserInfoServices:
    return UserInfoServices(
        jwt=jwt,
        user_repo=user_repo,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
    )


def provide_login_form_service_stub() -> None:
    ...


def provide_login_form_service(
    client_repo: ClientRepository,
) -> LoginFormService:
    return LoginFormService(client_repo=client_repo)


def provide_admin_auth_service_stub() -> None:
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


def provide_device_service_stub() -> None:
    ...


def provide_device_service(
    client_repo: ClientRepository,
    device_repo: DeviceRepository,
) -> DeviceService:
    return DeviceService(client_repo=client_repo, device_repo=device_repo)
