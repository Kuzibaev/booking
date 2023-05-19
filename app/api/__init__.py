from fastapi import APIRouter

from app.core import app_dependencies
from .client import router as client_router
from .media import router as media_router
from .merchant import merchant_app

router = APIRouter(dependencies=app_dependencies)
router.include_router(media_router)
router.mount("/merchant", app=merchant_app)
router.include_router(client_router)
