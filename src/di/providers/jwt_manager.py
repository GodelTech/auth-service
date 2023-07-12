from src.business_logic.jwt_manager import JWTManager
from src.business_logic.jwt_manager.interfaces import JWTManagerProtocol



def provide_jwt_manager_stub() -> None:
    ...


def provide_jwt_manager() -> JWTManagerProtocol:
    return JWTManager()
