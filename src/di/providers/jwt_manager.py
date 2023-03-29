from src.business_logic.jwt_manager import JWTManager
from src.business_logic.jwt_manager.interfaces import JWTServiceProto


def provide_jwt_manager_stub() -> None:
    ...


def provide_jwt_manager() -> JWTServiceProto:
    return JWTManager()
