from collections import OrderedDict
from typing import (
    Optional,
    Sequence,
    Type,
    Union,
    OrderedDict as OrderedDictType
)

from fastapi import Request
from sqladmin import Admin, BaseView, ModelView
from sqladmin._types import ENGINE_TYPE  # noqa
from sqladmin.authentication import AuthenticationBackend
from starlette.applications import Starlette
from starlette.middleware import Middleware


class MyBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        phone, password = form['username'], form['password']
        if phone != '+998901111212' or password != 'gtast!35s':  # noqa
            return False
        request.session.update({"token": "..."})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session


class CustomAdmin(Admin):
    def __init__(
            self,
            app: Starlette,
            engine: ENGINE_TYPE,
            base_url: str = "/admin",
            title: str = "Admin",
            logo_url: str = None,
            middlewares: Optional[Sequence[Middleware]] = None,
            debug: bool = False,
            templates_dir: str = "templates",
            authentication_backend: Optional[AuthenticationBackend] = None,
    ) -> None:
        super(CustomAdmin, self).__init__(
            app,
            engine,
            base_url,
            title,
            logo_url,
            middlewares,
            debug,
            templates_dir,
            authentication_backend
        )
        self._views_as_dict: OrderedDictType[str, list[Union[BaseView, ModelView]]] = OrderedDict()

    def add_view(self, view: Union[Type[ModelView], Type[BaseView]], app_name: str = None) -> None:
        super(CustomAdmin, self).add_view(view)
        if not app_name:
            return
        app_name = app_name.replace("_", " ")
        if app_name in self._views_as_dict:
            self._views_as_dict[app_name].append(view())
        else:
            self._views_as_dict[app_name] = [view()]

    @property
    def views_as_dict(self) -> OrderedDictType[str, list[Union[BaseView, ModelView]]]:
        return self._views_as_dict
