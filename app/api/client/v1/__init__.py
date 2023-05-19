from fastapi import APIRouter

from .about_us import router as about_us_router
from .article import router as article_router
from .booking import router as booking_router
from .chat import router as chat_router
from .cities import router as cities_router
from .docs import router as doc_file_router
from .faq import router as faq_router
from .favourite import router as favourite_router
from .login import router as login_router
from .properties import router as properties_router
from .reviews import router as reviews_router
from .test import router as test_router
from .users import router as users_router
from .oauth import router as oauth_router

router = APIRouter()
router.include_router(test_router, tags=['Test'])
router.include_router(login_router, prefix='/login', tags=['Login'])
router.include_router(oauth_router, prefix='/oauth', tags=['OAuth'])
router.include_router(users_router, prefix='/user', tags=['Users'])
router.include_router(properties_router, prefix='/property', tags=['Property'])
router.include_router(favourite_router, prefix='/favourite', tags=['Favourite'])
router.include_router(cities_router, prefix='/city', tags=['City'])
router.include_router(article_router, prefix='/article', tags=['Article'])
router.include_router(about_us_router, prefix='/about-us', tags=['About'])
router.include_router(faq_router, prefix='/faq', tags=['Faq'])
router.include_router(doc_file_router, prefix='/doc', tags=['DocFile'])
router.include_router(booking_router, prefix='/booking', tags=['Booking'])
router.include_router(reviews_router, prefix='/review', tags=['Reviews'])
router.include_router(chat_router, prefix='/chat', tags=['Chat'])
