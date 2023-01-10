from typing import Optional
import hashlib
from fastapi import Request, Response

import logging

def builder_with_parametr(
    func,
    namespace: Optional[str] = "",
    request: Optional[Request] = None,
    response: Optional[Response] = None,
    args: Optional[tuple] = None,
    kwargs: Optional[dict] = None,
):
    logger = logging.getLogger("is_app")
    prefix = f"client-{request.client.host}"
    dict_to_encode = {k: kwargs[k] for k in kwargs.keys() if type(kwargs[k]) in (str, int, float, bool, dict, str, list)}

    cache_key = (
        prefix
        + hashlib.md5(  # nosec:B303
            f"{prefix}:{func.__module__}:{func.__name__}:{args}:{dict_to_encode}".encode()
        ).hexdigest()
    )
    logger.info(f"Redis key: {cache_key}")
    return cache_key