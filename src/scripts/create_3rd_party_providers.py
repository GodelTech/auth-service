from src.scripts.providers_data import PROVIDERS
from src.data_access.postgresql.repositories import ThirdPartyOIDCRepository


class CreateIndentityProvidersFromConfig:
    def __init__(
        self,
        providers_repo: ThirdPartyOIDCRepository,
        config_data: list[dict[str, str]] = PROVIDERS
    ) -> None:
        self.config_data = config_data
        self._providers_repo = providers_repo

    def execute(self) -> None:
        for row in self.config_data:
            provider_name = row.get("name")
            if not self._providers_repo.exists(name=provider_name):
                self._providers_repo.create(
                    name=provider_name,
                    auth_endpoint_link=row.get("authorization_endpoint"),
                    token_endpoint_link=row.get("token_endpoint"),
                    userinfo_link=row.get("userinfo_endpoint"),
                    internal_redirect_uri=row.get("internal_redirect_link"),
                    provider_icon=row.get("icon")
                )
