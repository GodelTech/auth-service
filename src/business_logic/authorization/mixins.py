from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.business_logic.authorization.dto import AuthRequestModel

    from .interfaces import HasUserRepoProtocol


class UpdateRedirectUrlMixin:
    """
    Mixin class for updating the redirect URL in an authentication system.

    This mixin provides a method to update the redirect URL with additional parameters,
    such as the state parameter.
    """

    async def _update_redirect_url(
        self: HasUserRepoProtocol,
        request_data: AuthRequestModel,
        redirect_url: str,
    ) -> str:
        """
        Update the redirect URL with additional parameters.

        Args:
            request_data: An instance of AuthRequestModel containing the request data.
            redirect_url: The original redirect URL.

        Returns:
            The updated redirect URL with additional parameters.

        """
        if request_data.state:
            redirect_url += f"&state={request_data.state}"
        return redirect_url
