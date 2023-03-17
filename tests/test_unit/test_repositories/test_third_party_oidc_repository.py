import pytest
from sqlalchemy import insert, delete

from src.data_access.postgresql.errors import (
    ThirdPartyStateNotFoundError,
    ThirdPartyStateDuplicationError,
)
from src.data_access.postgresql.repositories import ThirdPartyOIDCRepository
from src.data_access.postgresql.tables import IdentityProviderMapped
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
class TestThirdPartyRepository:
    async def test_get_row_providers_data(self, engine, connection):
        oidc_repo = ThirdPartyOIDCRepository(engine)
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=1,
                provider_client_id="test_client",
                provider_client_secret="secret",
                enabled=True,
            )
        )
        await connection.commit()
        providers = await oidc_repo.get_row_providers_data()
        assert len(providers) == 1
        assert providers[0][2] == "test_client"
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.provider_client_id == "test_client"
            )
        )
        await connection.commit()

    async def test_get_row_providers_data_not_exist(
        self, engine: AsyncEngine, connection: AsyncSession
    ) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        await connection.commit()
        providers = await oidc_repo.get_row_providers_data()
        assert len(providers) == 0
        assert providers == []

    async def test_get_row_provider_credentials_by_name(
        self, engine: AsyncEngine, connection: AsyncSession
    ) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        await connection.execute(
            insert(IdentityProviderMapped).values(
                identity_provider_id=1,
                provider_client_id="test_client",
                provider_client_secret="secret",
                enabled=True,
            )
        )
        await connection.commit()
        provider_data = await oidc_repo.get_row_provider_credentials_by_name(
            name="github"
        )
        assert provider_data is not None
        assert len(provider_data) == 3
        assert provider_data[0] == "test_client"
        assert provider_data[1] == "secret"
        await connection.execute(
            delete(IdentityProviderMapped).where(
                IdentityProviderMapped.provider_client_id == "test_client"
            )
        )
        await connection.commit()

    async def test_get_row_provider_data_by_not_registered_name(
        self, engine: AsyncEngine
    ) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        provider_data = await oidc_repo.get_row_provider_credentials_by_name(
            name="SomeNotRegisteredProvider"
        )
        assert provider_data is None

    async def test_get_provider_external_links(
        self, engine: AsyncEngine
    ) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        expected_token_link = "https://github.com/login/oauth/access_token"
        expected_user_link = "https://api.github.com/user"

        links = await oidc_repo.get_provider_external_links(name="github")
        assert links
        assert expected_token_link == links[0]
        assert expected_user_link == links[1]

    async def test_get_not_registered_provider_external_links(
        self, engine: AsyncEngine
    ) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        provider_data = await oidc_repo.get_provider_external_links(
            name="SomeNotRegisteredProvider"
        )
        assert provider_data is None

    async def test_create_validate_delete_state(
        self, engine: AsyncEngine
    ) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        await oidc_repo.create_state(state="some_state")
        valid = await oidc_repo.validate_state(state="some_state")
        assert valid is True
        await oidc_repo.delete_state(state="some_state")
        valid = await oidc_repo.validate_state(state="some_state")
        assert valid is False

    async def test_create_state_already_exists(
        self, engine: AsyncEngine
    ) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        await oidc_repo.create_state(state="some_state")

        valid = await oidc_repo.validate_state(state="some_state")
        assert valid is True

        with pytest.raises(ThirdPartyStateDuplicationError):
            await oidc_repo.create_state(state="some_state")
        await oidc_repo.delete_state(state="some_state")

    async def test_delete_state_not_exist(self, engine: AsyncEngine) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        with pytest.raises(ThirdPartyStateNotFoundError):
            await oidc_repo.delete_state(state="not_exist")

    async def test_validate_state_not_exists(self, engine: AsyncEngine) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        validated = await oidc_repo.validate_state("no_such_a_state")
        assert validated is False

    async def test_get_provider_id_by_name(self, engine: AsyncEngine) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        provider_id = await oidc_repo.get_provider_id_by_name(name="github")
        assert provider_id == 1

    async def test_get_not_registered_provider_id_by_name(
        self, engine: AsyncEngine
    ) -> None:
        oidc_repo = ThirdPartyOIDCRepository(engine)
        provider_id = await oidc_repo.get_provider_id_by_name(
            name="SomeNotRegisteredProvider"
        )
        assert provider_id is None
