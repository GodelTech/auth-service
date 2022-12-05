import secrets

from src.presentation.models.authorization import RequestModel
from src.data_access.postgresql.repositories.client import ClientRepository
from src.data_access.postgresql.repositories.user import UserRepository
from src.business_logic.services.password_service import PasswordHash

from src.data_access.postgresql.repositories.persistent_grant import PersistentGrantRepository


async def get_authorise(
        request: RequestModel,
        client_repo: ClientRepository,
        user_repo: UserRepository,
        persistent_grant_repo: PersistentGrantRepository
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
        else:
            raise Exception
    except Exception:
        raise 'Something wrong in get_authorisation_get'
