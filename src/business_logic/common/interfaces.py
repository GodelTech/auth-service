from typing import Protocol, Any


class ValidatorProto(Protocol):
    async def __call__(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError
