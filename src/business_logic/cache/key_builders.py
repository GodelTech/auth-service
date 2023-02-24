import hashlib
import logging
from typing import Optional, Callable, Any

from fastapi import Request, Response

logger = logging.getLogger(__name__)


def builder_with_parametr(
    func: Callable[..., Any],
    request: Optional[Request] = None,
    args: Optional[tuple[Any]] = None,
    kwargs: Optional[dict[Any, Any]] = None,
) -> str:
    if request is not None and request.client is not None:
        prefix = f"client-{request.client.host}"
        dict_to_encode : Optional[dict[Any, Any]] = None
        if kwargs is not None:
            dict_to_encode = {
                k: kwargs[k]
                for k in kwargs.keys()
                if type(kwargs[k]) in (str, int, float, bool, dict, str, list)
            }

        cache_key = (
            prefix
            + hashlib.md5(  # nosec:B303
                f"{prefix}:{func.__module__}:{func.__name__}:{args}:{dict_to_encode}".encode()
            ).hexdigest()
        )
        logger.info(f"Redis key: {cache_key}")
        return cache_key
    raise ValueError