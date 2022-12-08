import secrets
from fastapi import Depends

from src.presentation.api.models import RequestModel
from src.data_access.postgresql.repositories import ClientRepository, UserRepository, PersistentGrantRepository
from src.business_logic.services.password import PasswordHash
from src.data_access.postgresql.events import logger
from src.data_access.postgresql.errors import ClientNotFoundError, UserNotFoundError, WrongPasswordError
from src.business_logic.dependencies import get_repository


async def get_authorise(
        request: RequestModel,
        client_repo: ClientRepository = Depends(get_repository(ClientRepository)),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        persistent_grant_repo: PersistentGrantRepository = Depends(get_repository(PersistentGrantRepository))
):
    try:
        client = await client_repo.get_client_by_client_id(client_id=request.client_id)
        if client:
            scope_data = {item.split('=')[0]: item.split('=')[1] for item in request.scope.split('&')[1:]}
            secret_code = secrets.token_urlsafe(32)
            password = scope_data['password']
            user_name = scope_data['username']

            user_hash_password = await user_repo.get_hash_password(user_name)

            validated = PasswordHash.validate_password(password, user_hash_password)

            if user_hash_password and validated:
                await persistent_grant_repo.create_new_grant(request.client_id, secret_code)
                redirect_uri = f"{request.redirect_uri}?code={secret_code}"
                if request.state:
                    redirect_uri += f"&state={request.state}"

                return redirect_uri
    except ClientNotFoundError as exception:
        logger.exception(exception)
    except UserNotFoundError as exception:
        logger.exception(exception)
    except KeyError as exception:
        message = f"KeyError: key {exception} does not exist is not in the scope"
        logger.exception(message)
    except IndexError as exception:
        message = f"IndexError: {exception} - Impossible to parse the scope"
        logger.exception(message)


class AuthorisationService:
    def __init__(
        self, 
        client_repo: ClientRepository = Depends(get_repository(ClientRepository)),
        user_repo: UserRepository = Depends(get_repository(UserRepository)),
        persistent_grant_repo: PersistentGrantRepository = Depends(get_repository(PersistentGrantRepository)),
        password_service: PasswordHash = Depends()
    ) -> None:
        self._request = None
        self.client_repo = client_repo
        self.user_repo = user_repo
        self.persistent_grant_repo = persistent_grant_repo
        self.password_service = password_service

    async def get_redirect_url(self) -> str:
        try:
            if await self._validate_client(self.request.client_id):
                scope_data = await self._parse_scope_data(scope=self.request.scope)
                password = scope_data['password']
                user_name = scope_data['username']
                
                user_hash_password, user_id = await self.user_repo.get_hash_password(user_name)
                validated = self.password_service.validate_password(password, user_hash_password)
                
                if user_hash_password and validated:
                    secret_code = secrets.token_urlsafe(32)
                    await self.persistent_grant_repo.create_new_grant(
                        client_id=self.request.client_id,
                        secret_code=secret_code,
                        user_id=user_id
                    )
                    
                    return await self._update_redirect_url_with_params(secret_code=secret_code)
        except ClientNotFoundError as exception:
            logger.exception(exception)
        except UserNotFoundError as exception:
            logger.exception(exception)
        except WrongPasswordError as exception:
            logger.exception(exception)
        except KeyError as exception:
            message = f"KeyError: key {exception} does not exist is not in the scope"
            logger.exception(message)
        except IndexError as exception:
            message = f"IndexError: {exception} - Impossible to parse the scope"
            logger.exception(message)

    async def _validate_client(self, client_id: str) -> bool:
        """
        Checks if the client is in the database.
        """
        client = await self.client_repo.get_client_by_client_id(client_id=client_id)
        return client
    
    async def _parse_scope_data(self, scope: str) -> dict:
        """
        """
        return {item.split('=')[0]: item.split('=')[1] for item in scope.split('&')[1:]}

    async def _update_redirect_url_with_params(self, secret_code: str) -> str:
        redirect_uri = f"{self.request.redirect_uri}?code={secret_code}"
        if self.request.state:
            redirect_uri += f"&state={self.request.state}"

        return redirect_uri

    @property
    def request(self) -> None:
        return self._request

    @request.setter
    def request(self, request: RequestModel) -> None:
        self._request = request

