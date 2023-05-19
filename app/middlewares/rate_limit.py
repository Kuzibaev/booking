from fastapi import Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

from app.utils.rate_limiter import RateLimitExceeded


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            response = await call_next(request)
        except RateLimitExceeded as exp:
            return JSONResponse(
                content={'ok': False, 'detail': 'Rate limit exceeded', 'retry_after': exp.time_left},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS
            )
        else:
            return response
