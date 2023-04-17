from typing import Protocol, Optional, Any
from typing import TYPE_CHECKING
# if TYPE_CHECKING:
from src.business_logic.endsession.dto import RequestEndSessionModel

class EndSessionServiceProtocol(Protocol):

    async def end_session(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def request_model(self) -> Optional[RequestEndSessionModel]:
        raise NotImplementedError

    @request_model.setter
    def request_model(self, request_model: RequestEndSessionModel) -> None:
        raise NotImplementedError

