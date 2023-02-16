import hashlib
import logging
from typing import Any, Callable, Dict, Optional, Tuple

from fastapi import Request, Response

logger = logging.getLogger(__name__)


def builder_with_parameter(
    func: Callable[[Any], Any],
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[Tuple[Any]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    if (
        request is not None
        and kwargs is not None
        and request.client is not None
    ):
        prefix = f"client-{request.client.host}"
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
    return None
