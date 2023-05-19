from app.core.conf import settings

from .core import I18n

__all__ = [
    'I18n',
    'translation'
]

translation = I18n(domain=settings.get_project_name(), path=settings.LOCALES_DIR, default='en')
gettext = translation.gettext
lazy_gettext = translation.lazy_gettext
