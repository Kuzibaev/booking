from fastapi import APIRouter, Request

from app.core.conf import settings
from app.utils.i18n import translation

_ = translation.lazy_gettext

router = APIRouter()


@router.get('/test/')
async def test(request: Request):
    test_string = _("This is a test string")
    return {'status': 'ok', 'language': request.state.language, 'data': _('Hello world'), 'test': test_string,
            'debug': settings.DEBUG}
