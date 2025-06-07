import jwt
import pytest
from sqlalchemy import insert, select, delete

from src.data_access.postgresql.errors import ClientPostLogoutRedirectUriError
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.errors.persistent_grant import (
    PersistentGrantNotFoundError,
)

from tests.test_unit.fixtures import end_session_request_model, TOKEN_HINT_DATA
from src.business_logic.services.endsession import EndSessionService
from src.presentation.api.models.endsession import RequestEndSessionModel
from sqlalchemy.ext.asyncio.engine import AsyncEngine


@pytest.mark.asyncio
class TestEndSessionService:
    async def test_validate_logout_redirect_uri(
        self,
        end_session_service: EndSessionService,
        end_session_request_model: RequestEndSessionModel,
    ) -> None:
        service = end_session_service
        service.request_model = end_session_request_model
        if not service.request_model.post_logout_redirect_uri:
            raise AssertionError
        result = await service._validate_logout_redirect_uri(
            client_id="test_client",
            logout_redirect_uri=service.request_model.post_logout_redirect_uri,
        )

        assert result is True

    async def test_validate_logout_redirect_uri_error(
        self,
        end_session_service: EndSessionService,
        end_session_request_model: RequestEndSessionModel,
    ) -> None:
        service = end_session_service
        service.request_model = end_session_request_model
        service.request_model.post_logout_redirect_uri = "not_exist_uri"
        with pytest.raises(ClientPostLogoutRedirectUriError):
            await service._validate_logout_redirect_uri(
                client_id="client_not_exist",
                logout_redirect_uri=service.request_model.post_logout_redirect_uri,
            )
            a = 1

    async def test_logout(
        self,
        end_session_service: EndSessionService,
        end_session_request_model: RequestEndSessionModel,
        connection: AsyncEngine,
    ) -> None:
        service = end_session_service
        service.request_model = end_session_request_model
        await connection.execute(
            insert(PersistentGrant).values(
                key="test_key",
                client_id=1,
                user_id=2,
                grant_data="test_logout",
                persistent_grant_type_id=1,
                expiration=False,
            )
        )
        await connection.commit()

        await service._logout(client_id="test_client", user_id=2)
        grant = await connection.execute(
            select(PersistentGrant)
            .where(PersistentGrant.client_id == 1)
            .where(PersistentGrant.user_id == 2)
        )
        await connection.commit()
        assert grant.first() is None

    async def test_logout_account_not_exists(
        self,
        end_session_service: EndSessionService,
        end_session_request_model: RequestEndSessionModel,
    ) -> None:
        service = end_session_service
        service.request_model = end_session_request_model
        # Below check is temporary disabled to implement implicit flow logout
        # with pytest.raises(PersistentGrantNotFoundError):
        await service._logout(client_id="test_client", user_id=33333)

    async def test_decode_id_token_hint(
        self,
        end_session_service: EndSessionService,
        end_session_request_model: RequestEndSessionModel,
    ) -> None:
        service = end_session_service
        service.request_model = end_session_request_model
        data = await service._decode_id_token_hint(
            service.request_model.id_token_hint
        )

        assert data["sub"] == 3
        assert data["data"] == "secret_code"

    async def test_decode_id_token_hint_error(
        self, end_session_service: EndSessionService
    ) -> None:
        service = end_session_service
        with pytest.raises(jwt.exceptions.DecodeError):
            await service._decode_id_token_hint("abra$kadabra")

    async def test_end_session(
        self,
        end_session_service: EndSessionService,
        end_session_request_model: RequestEndSessionModel,
        connection: AsyncEngine,
    ) -> None:
        service = end_session_service
        service.request_model = end_session_request_model
        service.request_model.post_logout_redirect_uri = "https://www.cole.com/"
        await connection.execute(
            insert(PersistentGrant).values(
                key="test_key",
                client_id=3,
                user_id=3,
                grant_data="test_end_session",
                persistent_grant_type_id=1,
                expiration=False,
            )
        )
        await connection.commit()
        redirect_uri = await service.end_session()
        assert redirect_uri == "https://www.cole.com/&state=test_state"

        await connection.execute(
            delete(PersistentGrant).where(PersistentGrant.client_id == 1)
        )
        await connection.commit()

    async def test_end_session_without_state(
        self,
        end_session_service: EndSessionService,
        end_session_request_model: RequestEndSessionModel,
        connection: AsyncEngine,
    ) -> None:
        service = end_session_service
        service.request_model = end_session_request_model
        service.request_model.post_logout_redirect_uri = "https://www.cole.com/"
        service.request_model.state = None
        await connection.execute(
            insert(PersistentGrant).values(
                key="test_key",
                client_id=3,
                user_id=3,
                grant_data="test_end_session_without_state",
                persistent_grant_type_id=1,
                expiration=False,
            )
        )
        await connection.commit()
        redirect_uri = await service.end_session()
        assert redirect_uri == "https://www.cole.com/"

        await connection.execute(
            delete(PersistentGrant).where(PersistentGrant.client_id == 3)
        )
        await connection.commit()

    async def test_end_session_wrong_uri(
        self,
        end_session_service: EndSessionService,
        end_session_request_model: RequestEndSessionModel,
        connection: AsyncEngine,
    ) -> None:
        service = end_session_service
        service.request_model = end_session_request_model
        await connection.execute(
            insert(PersistentGrant).values(
                key="test_key",
                client_id=3,
                user_id=3,
                grant_data="test_end_session_wrong_uri",
                persistent_grant_type_id=1,
                expiration=False,
            )
        )
        await connection.commit()

        with pytest.raises(ClientPostLogoutRedirectUriError):
            await service.end_session()

        await connection.execute(
            delete(PersistentGrant).where(PersistentGrant.client_id == 3)
        )
        await connection.commit()
