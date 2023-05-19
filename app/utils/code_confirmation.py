import secrets
import string
from datetime import datetime

from app.core.conf import settings
from .redis_helper import RedisHelper


class CodeConfirmation(RedisHelper):
    PREFIX = 'code_confirmation'

    @staticmethod
    def generate_secret_token(length: int = 30):
        token = secrets.token_hex(length)
        t = str(int(datetime.utcnow().timestamp()))
        return token + t

    @staticmethod
    def generate_code(phone: str = None, length: int = 6):
        if settings.DEBUG or phone == settings.DEBUG_PHONE:
            return settings.DEBUG_SMS_CODE
        return ''.join([secrets.choice(string.digits) for _ in range(length)])

    @classmethod
    async def get_code(cls, phone: str) -> tuple[str, str]:
        token, code = cls.generate_secret_token(), cls.generate_code(phone)
        await cls.set_data(token, dict(phone=phone, code=code), settings.CODE_LIFETIME)
        return token, code

    @classmethod
    async def check_code(cls, token: str, code: str) -> str | bool | None:
        data = await cls.get_data(token)
        if code_ := data.get('code'):
            return data.get('phone') if code_ == code else False
        return
