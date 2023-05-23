from src.data_access.postgresql.tables.identity_resource import (
    IdentityProvider,
)
from scripts.populate_data.third_party_providers_config.providers_config import (
    IdentityProviderConfig,
)
from src.dyna_config import DOMAIN_NAME
from sqlalchemy import select


async def populate_identity_providers(session_factory) -> None:
    async with session_factory() as session:
        for provider_data in IdentityProviderConfig._providers_config:
            existing_provider = await session.execute(
                select(IdentityProvider).where(
                    IdentityProvider.name == provider_data.name
                )
            )
            if not existing_provider.first():
                provider = IdentityProvider(
                    name=provider_data.name,
                    auth_endpoint_link=provider_data.auth_endpoint_link,
                    token_endpoint_link=provider_data.token_endpoint_link,
                    userinfo_link=provider_data.userinfo_link,
                    internal_redirect_uri=provider_data.internal_redirect_uri,
                    provider_icon=provider_data.provider_icon,
                )
                session.add(provider)

        await session.commit()


google_provider_config = IdentityProviderConfig(
    name="google",
    auth_endpoint_link="https://accounts.google.com/o/oauth2/v2/auth",
    token_endpoint_link="https://oauth2.googleapis.com/token",
    userinfo_link="https://openidconnect.googleapis.com/v1/userinfo",
    internal_redirect_uri=f"{DOMAIN_NAME}/authorize/oidc/google",
    provider_icon="fa-google",
)

github_provider_config = IdentityProviderConfig(
    name="github",
    auth_endpoint_link="https://github.com/login/oauth/authorize",
    token_endpoint_link="https://github.com/login/oauth/access_token",
    userinfo_link="https://api.github.com/user",
    internal_redirect_uri=f"{DOMAIN_NAME}/authorize/oidc/github",
    provider_icon="fa-github",
)

gitlab_provider_config = IdentityProviderConfig(
    name="gitlab",
    auth_endpoint_link="https://gitlab.com/oauth/authorize",
    token_endpoint_link="https://gitlab.com/oauth/token",
    userinfo_link="https://gitlab.com/oauth/userinfo",
    internal_redirect_uri=f"{DOMAIN_NAME}/authorize/oidc/gitlab",
    provider_icon="fa-gitlab",
)

linkedin_provider_config = IdentityProviderConfig(
    name="linkedin",
    auth_endpoint_link="https://www.linkedin.com/oauth/v2/authorization",
    token_endpoint_link="https://www.linkedin.com/oauth/v2/accessToken",
    userinfo_link="https://api.linkedin.com/v2/userinfo",
    internal_redirect_uri=f"{DOMAIN_NAME}/authorize/oidc/linkedin",
    provider_icon="fa-linkedin",
)

microsoft_provider_config = IdentityProviderConfig(
    name="microsoft",
    auth_endpoint_link="https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize",
    token_endpoint_link="https://login.microsoftonline.com/consumers/oauth2/v2.0/token",
    userinfo_link="https://graph.microsoft.com/oidc/userinfo",
    internal_redirect_uri=f"{DOMAIN_NAME}/authorize/oidc/microsoft",
    provider_icon="fa-microsoft",
)
