from fastapi import APIRouter

from .chat import router as chat_router
from .contract import router as contract_router
from .dashboard import router as dashboard_router
from .login import router as login_router
from .personal import router as personal_router
from .properties import router as property_router
from .review import router as review_router
from .users import router as users_router
from .transactions import router as transaction_router

router = APIRouter()
router.include_router(login_router, prefix='/login', tags=['Login'])
router.include_router(users_router, prefix='/user', tags=['Users'])
router.include_router(dashboard_router, prefix="/dashboard", tags=['Dashboard'])
router.include_router(contract_router, prefix='/contract', tags=['Contract'])
router.include_router(personal_router, prefix='/personal', tags=['Personal'])
router.include_router(property_router, prefix='/property', tags=['Property'])

router.include_router(review_router, prefix='/review', tags=['Review'])
router.include_router(chat_router, prefix='/chat', tags=['Chat'])
router.include_router(transaction_router, prefix='/transaction', tags=['Transaction'])
