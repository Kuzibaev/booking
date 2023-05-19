import gettext as gettext_module
import os
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Dict, Generator

from .lazy_proxy import LazyProxy


class I18n:
    def __init__(self, domain='app', path=None, default='en'):
        if path is None:
            path = os.path.join(os.getcwd(), 'locales')
        self.domain = domain
        self.path = path
        self.default = default
        self.locales = self.find_locales()
        self.ctx_locale = ContextVar("ctx_app_locale", default=default)

    @property
    def current_locale(self) -> str:
        return self.ctx_locale.get()

    @current_locale.setter
    def current_locale(self, value: str) -> None:
        self.ctx_locale.set(value)

    @contextmanager
    def use_locale(self, locale: str) -> Generator[None, None, None]:
        """
        Create context with specified locale
        """
        ctx_token = self.ctx_locale.set(locale)
        try:
            yield
        finally:
            self.ctx_locale.reset(ctx_token)

    def find_locales(self) -> Dict[str, gettext_module.GNUTranslations]:
        """
        Load all compiled locales from path
        :return: dict with locales
        """
        translations = {}

        for name in os.listdir(self.path):
            if not os.path.isdir(os.path.join(self.path, name)):
                continue
            mo_path = os.path.join(self.path, name, 'LC_MESSAGES', self.domain + '.mo')

            if os.path.exists(mo_path):
                with open(mo_path, 'rb') as fp:
                    translations[name] = gettext_module.GNUTranslations(fp)
            # elif os.path.exists(mo_path[:-2] + 'po'):
            #     raise RuntimeError(f"Found locale '{name}' but this language is not compiled!")
        return translations

    def gettext(self, singular, plural=None, n=1, locale=None) -> str:
        """
        Get text
        :param singular:
        :param plural:
        :param n:
        :param locale:
        :return:
        """
        if locale is None:
            locale = self.current_locale

        if locale not in self.locales:
            if n == 1:
                return singular
            return plural

        translator = self.locales[locale]

        if plural is None:
            return translator.gettext(singular)
        return translator.ngettext(singular, plural, n)

    def lazy_gettext(self, singular, plural=None, n=1, locale=None, enable_cache=False) -> str:
        """
        Lazy get text
        :param singular:
        :param plural:
        :param n:
        :param locale:
        :param enable_cache:
        :return:
        """
        return str(LazyProxy(self.gettext, singular, plural, n, locale, enable_cache=enable_cache))

    def reload(self):
        """
        Hot reload locales
        """
        self.locales = self.find_locales()
