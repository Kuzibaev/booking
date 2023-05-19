import json
from json import JSONDecodeError

from app.core.conf import settings
from app.core.sessions import redis


class RedisHelper:
    PREFIX: str
    DELIMITER: str = ':'

    @classmethod
    def _make_cache_key(cls, unique_str: str, get_prefix_only: bool = False):
        parts = [
            settings.get_project_name(),
            cls.PREFIX,
        ]
        if get_prefix_only:
            return cls.DELIMITER.join(parts)
        return cls.DELIMITER.join([*parts, unique_str])

    @classmethod
    async def set_data(cls, key: str, data: dict, ex: int):
        await redis.set(cls._make_cache_key(key), json.dumps(data), ex=ex)

    @classmethod
    async def get_data(cls, key: str):
        data = await redis.get(cls._make_cache_key(key))
        if not data:
            return {}
        try:
            data = json.loads(data)
            return data
        except JSONDecodeError:
            return {}
