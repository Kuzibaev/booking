from app.core.conf import settings
from app.crud.oauth_base import OAuthBase
from app.models.enums import SocialType
from app.schemas.oauth import (
    OAuthUserDataResponseSchema,
    OAuthTokenResponseSchema,
    OAuthCodeResponseSchema,
    OAuthRedirectLink
)


class FacebookOAuth(OAuthBase):
    """
    Config Facebook

    https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow?locale=ru_RU#exchangecode
    """

    scope = ["email", "public_profile"]

    user_fields = ["id", "first_name", "last_name", "email"]

    def prepare_user_data(self, user_data: dict) -> OAuthUserDataResponseSchema:
        """Converting interface socials for the general data format of the system"""

        return OAuthUserDataResponseSchema(
            social_id=user_data['id'],
            email=user_data['email'],
            social_type=SocialType.FACEBOOK,
            first_name=user_data['first_name'],
            last_name=user_data['last_name']
        )

    def generate_link_for_code(self) -> OAuthRedirectLink:
        """
        Generating a link to a redirect to the service to receive a confirmation code.

        It is necessary for the user to further enter the service and receive a confirmation code from the service on
        Webhook.
        """

        params = dict(
            client_id=self.client_id,
            redirect_uri=self.webhook_redirect_uri,
            scope=self.scope_to_str(','),
            response_type=self.response_type
        )
        return OAuthRedirectLink(url=self._make_url("https://www.facebook.com/v12.0/dialog/oauth?", params))

    async def get_token(self, code: OAuthCodeResponseSchema) -> OAuthTokenResponseSchema:
        """Exchange of a confirmation code for a user token."""

        response = await self._request(
            'GET',
            'https://graph.facebook.com/v12.0/oauth/access_token',
            data=dict(
                code=code.code,
                client_id=self.client_id,
                client_secret=self.secret_key,
                redirect_uri=self.webhook_redirect_uri,
            )
        )
        return OAuthTokenResponseSchema(**response)

    async def get_user_data(self, token: OAuthTokenResponseSchema) -> OAuthUserDataResponseSchema:
        """Getting information about a user through an access token."""
        response = await self._request(
            'GET',
            url="https://graph.facebook.com/me",
            data=dict(
                fields=",".join(self.user_fields),
                access_token=token.access_token
            )
        )
        return self.prepare_user_data(response)


facebook_oauth = FacebookOAuth(
    client_id=settings.FACEBOOK_CLIENT_ID,
    secret_key=settings.FACEBOOK_SECRET_KEY,
    webhook_redirect_uri=settings.FACEBOOK_WEBHOOK_OAUTH_REDIRECT_URI
)
