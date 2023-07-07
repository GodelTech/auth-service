from src.data_access.postgresql import DatabaseSync
from src.data_access.postgresql.repositories import RSAKeysRepository
from src.config.rsa_keys.rsa_keys_service import RSAKeysService, RSA_keys
from src.dyna_config import DB_URL

def provide_rsa_keys_stub() -> None:
    ...


def provide_rsa_keys() -> RSA_keys:
    db_url = DB_URL.replace("+asyncpg",'')
    sync_session_factory = DatabaseSync(database_url=db_url).sync_session_factory
    rsa_keys = RSAKeysService(
        sync_session_factory=sync_session_factory,
        rsa_keys_repo=RSAKeysRepository()
    ).get_rsa_keys()
    return rsa_keys
