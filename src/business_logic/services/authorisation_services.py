from fastapi import Depends
import traceback

from src.presentation.models.authorization import ResponseAuthorizationModel, PostRequestModel
from src.data_access.postgresql.repositories.client import ClientRepository


async def get_authorise(client_id: str, scope: str, repo: ClientRepository):
    try:
        client = await repo.get_client_by_client_id(client_id=client_id)

        if client:
            scope_data = {item.split('=')[0]: item.split('=')[1] for item in scope.split('&')[1:]}
            return True
            # password = data['password']
            # user_name = data['user_name']
            # access_code = repo.generate_code_by_user_name_and_password(password=password, user_name=user_name)
        else:
            return False
    except Exception:
        raise 'Something wrong in get_authorisation_get'

