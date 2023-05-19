import urllib.parse

from app.core.conf import settings
from app.crud.oauth_base import OAuthBase
from app.models.enums import SocialType
from app.schemas.oauth import (
    OAuthUserDataResponseSchema,
    OAuthTokenResponseSchema,
    OAuthRedirectLink
)


class GoogleOAuth(OAuthBase):
    """
    Config Google

    https://developers.google.com/identity/protocols/oauth2/web-server#httprest_3
    """

    scope = [
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    access_type = "offline"
    grand_type = 'authorization_code'

    def generate_body_for_access_token(self, code: str) -> dict:
        """Generating the request body to send to the service to receive the user's token."""
        return dict(
            code=code,
            client_id=self.client_id,
            client_secret=self.secret_key,
            grant_type=self.grand_type,
            redirect_uri=self.webhook_redirect_uri
        )

    def prepare_user_data(self, user_data: dict) -> OAuthUserDataResponseSchema:
        """Converting interface socials for the general data format of the system"""

        return OAuthUserDataResponseSchema(
            social_id=user_data['id'],
            email=user_data['email'],
            social_type=SocialType.GOOGLE,
            photo=user_data['picture'],
            first_name=user_data['name'],
            last_name=user_data['given_name']
        )

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.

        It is necessary for the user to further enter the service and receive a confirmation code from the service on Webhook.
        """

        url = "https://accounts.google.com/o/oauth2/v2/auth?"
        params = dict(
            scope=self.scope_to_str(),
            access_type=self.access_type,
            response_type=self.response_type,
            redirect_uri=self.webhook_redirect_uri,
            client_id=self.client_id,
            include_granted_scopes='true',
        )
        return OAuthRedirectLink(url=self._make_url(url, params))

    async def get_token(self, code: str) -> OAuthTokenResponseSchema:
        code = urllib.parse.unquote(code)
        """Exchange of a confirmation code for a user token."""
        response = await self._request(
            'POST',
            "https://oauth2.googleapis.com/token",
            data=self.generate_body_for_access_token(code),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return OAuthTokenResponseSchema(**response)

    async def get_user_data(self, token: OAuthTokenResponseSchema) -> OAuthUserDataResponseSchema:
        """"Getting information about a user through an access token."""
        response = await self._request(
            'GET',
            url="https://www.googleapis.com/userinfo/v2/me",
            headers={'Authorization': f'Bearer {token.access_token}'}
        )
        return self.prepare_user_data(response)


google_oauth = GoogleOAuth(
    client_id=settings.GOOGLE_CLIENT_ID,
    secret_key=settings.GOOGLE_SECRET_KEY,
    webhook_redirect_uri=settings.GOOGLE_WEBHOOK_OAUTH_REDIRECT_URI
)
