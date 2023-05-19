from .redis_helper import RedisHelper


class JWTToken(RedisHelper):
    PREFIX = 'jwt-token'

    @classmethod
    async def is_blacklisted(cls, token: str):
        if await cls.get_data(token):
            return True
        return False

    @classmethod
    async def blacklist_token(cls, token: str, ex: int):
        await cls.set_data(token, dict(blacklisted=True), ex=ex)
