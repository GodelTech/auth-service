from typing import Protocol, Any


class ValidatorProtocol(Protocol):
    async def __call__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError
