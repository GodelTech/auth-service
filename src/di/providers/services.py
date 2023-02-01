from src.data_access.postgresql.repositories import (
    ClientRepository,
    PersistentGrantRepository,
    UserRepository
)
from src.business_logic.services import (
    AuthorizationService,
    PasswordHash,
    EndSessionService,
    JWTService,
    TokenService,
    IntrospectionServies,
    UserInfoServices,
    LoginFormService
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


def provide_password_service():
    return PasswordHash()


def provide_endsession_service_stub():
    ...


def provide_endsession_service(
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
        jwt_service: JWTService
):
    return EndSessionService(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        jwt_service=jwt_service
    )


def provide_jwt_service_stub():
    ...


def provide_jwt_service():
    return JWTService()


def provide_introspection_service_stub():
    ...


def provide_introspection_service(
        jwt: JWTService,
        # token_service: TokenService,
        user_repo: UserRepository,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository
):
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
):
    return TokenService(
        client_repo=client_repo,
        persistent_grant_repo=persistent_grant_repo,
        user_repo=user_repo,
        jwt_service=jwt_service
    )


def provide_userinfo_service_stub():
    ...


def provide_userinfo_service(
        jwt: JWTService,
        # token_service: TokenService,
        user_repo: UserRepository,
        client_repo: ClientRepository,
        persistent_grant_repo: PersistentGrantRepository,
):
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
):
    return LoginFormService(
        client_repo=client_repo
    )


