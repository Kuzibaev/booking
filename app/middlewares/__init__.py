from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from app.core.conf import settings
from .rate_limit import RateLimitMiddleware

middleware = [
    Middleware(RateLimitMiddleware)
]

if settings.BACKEND_CORS_ORIGINS:
    middleware += [
        Middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
