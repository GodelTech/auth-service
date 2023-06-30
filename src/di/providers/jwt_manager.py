from src.di.providers.rsa_keys import provide_rsa_keys
from src.business_logic.jwt_manager import JWTManager
from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol



def provide_jwt_manager_stub() -> None:
    ...


def provide_jwt_manager() -> JWTManagerProtocol:
    rsa_keys = provide_rsa_keys()
    return JWTManager(keys=rsa_keys)
