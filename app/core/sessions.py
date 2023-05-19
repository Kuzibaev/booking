from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .conf import settings

redis = Redis.from_url(settings.REDIS_URL)
database = create_async_engine(
    settings.DB_CONFIG,
    future=False,
    echo=False,
)

AsyncSessionLocal = sessionmaker(bind=database, autoflush=False, expire_on_commit=False, class_=AsyncSession)


async def close():
    await database.dispose()
    await redis.close()


async def check_connections():
    redis.ping()
