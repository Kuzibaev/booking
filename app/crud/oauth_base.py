import json
import urllib.parse
from typing import List

import httpx

from app.schemas.oauth import (
    OAuthUserDataResponseSchema,
    OAuthTokenResponseSchema,
    OAuthCodeResponseSchema,
    OAuthRedirectLink
)


class BadRequest(Exception):
    def __init__(self, error: str = None, error_description: str = None):
        self.error = error
        self.error_description = error_description
        super().__init__(error, error_description)

    @classmethod
    def from_dict(cls, r: dict):
        return cls(error=r.get('error'), error_description=r.get('error_description'))

    def as_dict(self):
        return dict(error=self.error, error_description=self.error_description)


class OAuthBase:
    client_id: str
    secret_key: str
    webhook_redirect_uri: str

    scope: List[str]
    response_type: str = "code"

    def __init__(self, client_id: str, secret_key: str, webhook_redirect_uri: str) -> None:
        self.client_id = client_id
        self.secret_key = secret_key
        self.webhook_redirect_uri = webhook_redirect_uri

    @staticmethod
    async def _request(method: str, url: str, data: dict = None, headers: dict = None):
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, data=data, headers=headers)
            try:
                r_json = response.json()
            except json.JSONDecodeError:
                r_json = {}
            if response.status_code == 400:
                raise BadRequest.from_dict(r_json)
            return r_json

    @staticmethod
    def _make_url(url: str, params: dict = None):
        if not url.endswith("?"):
            url += "?"
        if params:
            url += urllib.parse.urlencode(params)
        return url

    def scope_to_str(self, delimiter: str = " ") -> str:
        """
        Convert a scope list to string representation

        Replacing spaces with encoded spaces% 20 for pydantic model validation
        """

        return f"{delimiter}".join(self.scope)

    def prepare_user_data(self, user_data: dict) -> OAuthUserDataResponseSchema:
        """Converting interface socials for the general data format of the system"""

        raise NotImplementedError

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.

        It is necessary for the user to further enter the service and receive a confirmation code from the service on Webhook.
        """

        raise NotImplementedError

    async def get_token(self, code: OAuthCodeResponseSchema) -> OAuthTokenResponseSchema:
        """Exchange of a confirmation code for a user token."""

        raise NotImplementedError

    async def get_user_data(self, token: OAuthTokenResponseSchema) -> OAuthUserDataResponseSchema:
        """"Getting information about a user through an access token."""

        raise NotImplementedError
