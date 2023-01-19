import jwt
import pytest
from sqlalchemy import insert, select

from src.data_access.postgresql.errors import (
    ClientPostLogoutRedirectUriError
)
from src.data_access.postgresql.tables.persistent_grant import PersistentGrant
from src.data_access.postgresql.errors.persistent_grant import PersistentGrantNotFoundError

from tests.test_unit.fixtures import end_session_request_model, TOKEN_HINT_DATA


@pytest.mark.asyncio
class TestEndSessionService:

    async def test_validate_logout_redirect_uri(self, end_session_service, end_session_request_model):
        service = end_session_service
        service.request_model = end_session_request_model
        result = await service._validate_logout_redirect_uri(
            client_id='test_client',
            logout_redirect_uri=service.request_model.post_logout_redirect_uri
        )

        assert result is True

    async def test_validate_logout_redirect_uri_error(self, end_session_service, end_session_request_model):
        service = end_session_service
        service.request_model = end_session_request_model
        service.request_model.post_logout_redirect_uri = 'not_exist_uri'
        with pytest.raises(ClientPostLogoutRedirectUriError):
            await service._validate_logout_redirect_uri(
                client_id='client_not_exist',
                logout_redirect_uri=service.request_model.post_logout_redirect_uri
            )

    async def test_logout(self, end_session_service, end_session_request_model):
        service = end_session_service
        service.request_model = end_session_request_model
        await service._logout(client_id='double_test', user_id=2, data='secret_code', grant_type='code')
        grant = await service.persistent_grant_repo.session.execute(
            select(PersistentGrant).
            where(PersistentGrant.client_id == 'double_test').
            where(PersistentGrant.subject_id == 2)
        )
        assert grant.first() is None

    async def test_logout_account_not_exists(self, end_session_service, end_session_request_model):
        service = end_session_service
        service.request_model = end_session_request_model
        with pytest.raises(PersistentGrantNotFoundError):
            await service._logout(
                client_id='test_client',
                user_id=33333,
                data='no_data',
                grant_type='no_code'
            )

    async def test_decode_id_token_hint(self, end_session_service, end_session_request_model):
        service = end_session_service
        service.request_model = end_session_request_model
        data = await service._decode_id_token_hint(service.request_model.id_token_hint)

        assert data["user_id"] == 3
        assert data["data"] == "secret_code"

    async def test_decode_id_token_hint_error(self, end_session_service):
        service = end_session_service
        with pytest.raises(jwt.exceptions.DecodeError):
            data = await service._decode_id_token_hint("abra$kadabra")

    async def test_end_session(self, end_session_service, end_session_request_model):
        service = end_session_service
        service.request_model = end_session_request_model
        service.request_model.post_logout_redirect_uri = "http://www.jones.com/"
        grant = await service.persistent_grant_repo.session.execute(
            insert(PersistentGrant).values(
                key="test_key",
                client_id=TOKEN_HINT_DATA["client_id"],
                subject_id=TOKEN_HINT_DATA["user_id"],
                data=TOKEN_HINT_DATA["data"],
                type=TOKEN_HINT_DATA["type"],
                expiration=False
            )
        )
        await service.persistent_grant_repo.session.commit()
        redirect_uri = await service.end_session()
        assert redirect_uri == 'http://www.jones.com/&state=test_state'

    async def test_end_session_without_state(self, end_session_service, end_session_request_model):
        service = end_session_service
        service.request_model = end_session_request_model
        service.request_model.post_logout_redirect_uri = "http://www.jones.com/"
        service.request_model.state = None
        grant = await service.persistent_grant_repo.session.execute(
            insert(PersistentGrant).values(
                key="test_key",
                client_id=TOKEN_HINT_DATA["client_id"],
                subject_id=TOKEN_HINT_DATA["user_id"],
                data=TOKEN_HINT_DATA["data"],
                type=TOKEN_HINT_DATA["type"],
                expiration=False
            )
        )
        await service.persistent_grant_repo.session.commit()
        redirect_uri = await service.end_session()
        assert redirect_uri == 'http://www.jones.com/'

    async def test_end_session_wrong_uri(self, end_session_service, end_session_request_model):
        service = end_session_service
        service.request_model = end_session_request_model
        grant = await service.persistent_grant_repo.session.execute(
            insert(PersistentGrant).values(
                key="test_key",
                client_id=TOKEN_HINT_DATA["client_id"],
                subject_id=TOKEN_HINT_DATA["user_id"],
                data=TOKEN_HINT_DATA["data"],
                type=TOKEN_HINT_DATA["type"],
                expiration=False
            )
        )
        await service.persistent_grant_repo.session.commit()

        with pytest.raises(ClientPostLogoutRedirectUriError):
            redirect_uri = await service.end_session()
