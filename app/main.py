import logging
from importlib import import_module
from inspect import getmembers, isclass

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqladmin import BaseView
from sqlalchemy.exc import SQLAlchemyError

from app.admin.base import MyBackend, CustomAdmin
from app.api import router
from app.core import sessions
from app.core.conf import settings, APP_DIR
from app.middlewares import middleware
from app.utils.exceptions import (
    parse_sqlalchemy_exc,
    DatabaseValidationError,
    database_validation_exception_handler
)

logger = logging.getLogger("uvicorn.error")


def init_admin_panel(app_: FastAPI):
    admin_panel = CustomAdmin(
        app_,
        engine=sessions.database,
        authentication_backend=MyBackend(secret_key=settings.SECRET_KEY),
        debug=settings.DEBUG
    )

    admin_module = 'admin'
    files_path = APP_DIR / admin_module
    files = list(files_path.glob('*.py'))
    files.sort(key=lambda f: f.stem)
    for file in files:
        file_path_with_dot = '.'.join([APP_DIR.stem, admin_module, file.stem])
        file_ = import_module(file_path_with_dot)
        for _, obj in getmembers(file_, predicate=isclass):
            if issubclass(obj, BaseView) and obj.__module__ == file_path_with_dot:
                admin_panel.add_view(obj, app_name=file.stem.capitalize())


async def on_shutdown():
    logger.info("shutdown")
    await sessions.close()


async def sqlalchemy_exp_handler(_, exception: SQLAlchemyError):
    logger.exception(exception)
    return JSONResponse(
        status_code=500,
        content={
            'ok': False,
            'detail': parse_sqlalchemy_exc(exception)
        }
    )


async def pydantic_exp_handler(request: Request, exception: ValidationError):
    logger.error(
        (
            f'url={request.url} exception={exception.__str__()}'
        )
    )
    return JSONResponse({
        'ok': False,
        'detail': f'Pydantic error: {exception.__str__()}'
    }, status_code=500)


app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    routes=router.routes,
    middleware=middleware,
    on_shutdown=[on_shutdown],
    exception_handlers={
        SQLAlchemyError: sqlalchemy_exp_handler,
        ValidationError: pydantic_exp_handler,
        DatabaseValidationError: database_validation_exception_handler,
    },
)
init_admin_panel(app)
