from typing import Any, Dict

from fastapi import status
from fastapi.responses import JSONResponse


class ErrorResponseBase(JSONResponse):
    @staticmethod
    def get_exception_detail(error: str, error_desc: str) -> Dict[str, str]:
        return {"error": error, "error_description": error_desc}


class InvalidRequestResponse(ErrorResponseBase):
    detail = ErrorResponseBase.get_exception_detail(
        error="invalid_request",
        error_desc="The request was missing required parameter(s).",
    )

    def __init__(self, detail: Any = detail) -> None:
        super().__init__(
            content=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnsupportedGrantTypeResponse(ErrorResponseBase):
    detail = ErrorResponseBase.get_exception_detail(
        error="unsupported_grant_type",
        error_desc="Requested grant type was not recognized by server.",
    )

    def __init__(self, detail: Any = detail) -> None:
        super().__init__(
            content=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class UnauthorizedClientResponse(ErrorResponseBase):
    detail = ErrorResponseBase.get_exception_detail(
        error="unauthorized_client",
        error_desc="The client is not authorized to use the requested grant type.",
    )

    def __init__(self, detail: Any = detail) -> None:
        super().__init__(
            content=detail,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InvalidClientResponse(ErrorResponseBase):
    detail = ErrorResponseBase.get_exception_detail(
        error="invalid_client",
        error_desc="Client authentication failed.",
    )

    def __init__(self, detail: Any = detail) -> None:
        super().__init__(
            content=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class InvalidGrantResponse(ErrorResponseBase):
    detail = ErrorResponseBase.get_exception_detail(
        error="invalid_grant",
        error_desc="Provided grant is invalid or expired.",
    )

    def __init__(self, detail: Any = detail) -> None:
        super().__init__(
            content=detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
