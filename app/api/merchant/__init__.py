from fastapi import FastAPI

from app.core import app_dependencies
from app.core.conf import settings
from app.middlewares import middleware
from .v1 import router as v1_router

merchant_app = FastAPI(
    title="Merchant API",
    debug=settings.DEBUG,
    middleware=middleware,
    dependencies=app_dependencies

)
merchant_app.state.is_merchant = True

merchant_app.include_router(v1_router, prefix='/api/v1')
