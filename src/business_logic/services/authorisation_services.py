from fastapi import Depends
import traceback

from src.presentation.models.authorization import ResponseAuthorizationModel, PostRequestModel
from src.data_access.postgresql.repositories.client import ClientRepository
from src.business_logic.dependencies.database import get_repository


async def get_authorisation_get(client_id, repo: ClientRepository):
    print('??????????????????????????????????', repo, client_id)
    try:
        print('---------------------', repo, client_id)

        client = await repo.get_client_by_client_id(client_id=client_id)
        print('=========================', client)

        if client:
            return True
        else:
            return False
    except Exception:
        print(traceback.format_exc())
        raise 'Something wrong in get_authorisation_get'




# def get_authorisation_put(request_data):
#     try:
#         user = ClientRepository.get_user_by_client_id(request_data.client_id)
#     except Exception:
#         raise 'Something wrong with put'

