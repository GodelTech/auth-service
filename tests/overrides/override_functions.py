from src.di.providers import (
    provide_config,
    provide_db,
    provide_auth_service,
    provide_password_service,
    provide_endsession_service,
    provide_client_repo,
    provide_user_repo,
    provide_persistent_grant_repo,
    provide_jwt_service,
    provide_introspection_service,
    provide_token_service,
    provide_userinfo_service,
    provide_login_form_service,
)


database_url = "postgresql+asyncpg://test:test@localhost:5463/test"
max_connection_count = 10
db_engine = provide_db(
    database_url=database_url, max_connection_count=max_connection_count
)

nodepends_provide_auth_service_override = lambda: provide_auth_service(
    client_repo=provide_client_repo(db_engine),
    user_repo=provide_user_repo(db_engine),
    persistent_grant_repo=provide_persistent_grant_repo(db_engine),
    password_service=provide_password_service(),
    jwt_service=provide_jwt_service(),
)

nodepends_provide_endsession_servise_override = (
    lambda: provide_endsession_service(
        client_repo=provide_client_repo(db_engine),
        persistent_grant_repo=provide_persistent_grant_repo(db_engine),
        jwt_service=provide_jwt_service(),
    )
)

nodepends_provide_introspection_service_override = lambda: provide_introspection_service(
    jwt=provide_jwt_service(),
    # token_service=provide_token_service(),
    user_repo=provide_user_repo(db_engine),
    client_repo=provide_client_repo(db_engine),
    persistent_grant_repo=provide_persistent_grant_repo(db_engine),
)

nodepends_provide_token_service_override = lambda: provide_token_service(
    jwt_service=provide_jwt_service(),
    user_repo=provide_user_repo(db_engine),
    client_repo=provide_client_repo(db_engine),
    persistent_grant_repo=provide_persistent_grant_repo(db_engine),
)

nodepends_provide_userinfo_service_override = lambda: provide_userinfo_service(
    jwt=provide_jwt_service(),
    user_repo=provide_user_repo(db_engine),
    client_repo=provide_client_repo(db_engine),
    persistent_grant_repo=provide_persistent_grant_repo(db_engine),
)

nodepends_provide_login_form_service_override = (
    lambda: provide_login_form_service(
        client_repo=provide_client_repo(db_engine)
    )
)
