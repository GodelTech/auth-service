import secrets

from fastapi import Depends
import traceback

from src.presentation.models.authorization import ResponseAuthorizationModel, PostRequestModel
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.user import UserRepository
from src.business_logic.services.password_service import PasswordHash
from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository


async def get_authorise(
        client_id: str,
        response_type: str,
        scope: str,
        redirect_uri: str,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository
):

    try:
        client = await client_repo.get_client_by_client_id(client_id=client_id)
        if client:
            scope_data = {item.split('=')[0]: item.split('=')[1] for item in scope.split('&')[1:]}
            secret_code = secrets.token_urlsafe(32)
            password = scope_data['password']
            user_name = scope_data['user_name']
            user_hash_password = user_repo.get_hash_password(user_name)
            if user_hash_password and PasswordHash.validate_password(password, user_hash_password):
                persistent_grant_repo.create_new_grant(client_id, secret_code)

            # access_code = await repo.generate_code_by_user_name_and_password(
            # client_id=client_id,
            # password=password,
            # user_name=user_name
            # )
        else:
            return False
    except Exception:
        raise 'Something wrong in get_authorisation_get'

