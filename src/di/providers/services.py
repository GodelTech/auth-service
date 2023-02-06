from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository,
    GroupRepository,
    RoleRepository,
)
from src.business_logic.services import (
    AuthorizationService,
    PasswordHash,
    EndSessionService,
    JWTService,
    TokenService,
    IntrospectionServies,
    UserInfoServices,
    LoginFormService,
    AdminUserService,
    AdminGroupService,
    AdminRoleService,
    AdminAuthService
)


def provide_auth_service_stub():
    ...


def provide_auth_service(
    client_repo: ClientRepository,
    user_repo: UserRepository,
    persistent_grant_repo: PersistentGrantRepository,
    password_service: PasswordHash,
    jwt_service: JWTService
):
    return AuthorizationService(
        client_repo=client_repo,
        user_repo=user_repo,
        persistent_grant_repo=persistent_grant_repo,
        password_service=password_service,
        jwt_service=jwt_service
    )


def provide_password_service_stub():
    ...


def provide_password_service() -> PasswordHash:
    return PasswordHash()


def provide_endsession_service_stub():
    ...


def provide_endsession_service(
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        jwt_service: JWTService
) -> EndSessionService:
    return EndSessionService(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        jwt_service=jwt_service
    )


def provide_jwt_service_stub():
    ...


def provide_jwt_service() -> JWTService:
    return JWTService()


def provide_introspection_service_stub():
    ...


def provide_introspection_service(
        jwt: JWTService,
        # token_service: TokenService,
        user_repo: UserRepository,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository
) -> IntrospectionServies:
    return IntrospectionServies(
        jwt=jwt,
        # token_service=token_service,
        user_repo=user_repo,
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo
    )


def provide_token_service_stub():
    ...


def provide_token_service(
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        user_repo: UserRepository,
        jwt_service: JWTService
) -> TokenService:
    return TokenService(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
        jwt_service=jwt_service
    )



def provide_admin_user_service_stub():
    ...

def provide_admin_user_service(
        user_repo: UserRepository,
):
    return AdminUserService(
        user_repo=user_repo,
    )



def provide_admin_group_service_stub():
    ...

def provide_admin_group_service(
        group_repo: GroupRepository,
):
    return AdminGroupService(
        group_repo=group_repo,
    )


def provide_admin_role_service_stub():
    ...

def provide_admin_role_service(
        role_repo: RoleRepository,
):
    return AdminRoleService(
        role_repo=role_repo,
    )


def provide_userinfo_service_stub():
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


def provide_login_form_service_stub():
    ...


def provide_login_form_service(
    client_repo: ClientRepository,
) -> LoginFormService:
    return LoginFormService(
        client_repo=client_repo
    )


def provide_admin_auth_service_stub():
    ...


def provide_admin_auth_service(
    user_repo: UserRepository,
    password_service: PasswordHash,
    jwt_service: JWTService
) -> AdminAuthService:
    return AdminAuthService(
        user_repo=user_repo,
        password_service=password_service,
        jwt_service=jwt_service
    )
