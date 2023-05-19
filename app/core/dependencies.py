# Some lines of code in this file are copied from https://github.com/lesnik512/fast-api-sqlalchemy-template

from contextvars import ContextVar
from typing import Optional

from fastapi import Request, Header, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.i18n import translation
from .conf import settings
from .sessions import AsyncSessionLocal

session_context_var: ContextVar[Optional[AsyncSessionLocal]] = ContextVar("_session", default=None)


async def set_db():
    """Store db session in the context var and reset it"""
    db = AsyncSessionLocal()
    token = session_context_var.set(db)
    try:
        yield
    except (SQLAlchemyError, HTTPException) as e:
        await db.rollback()
        raise e
    finally:
        await db.close()
        session_context_var.reset(token)


def get_db() -> AsyncSession:
    session = session_context_var.get()
    if session is None:
        raise Exception("Session is missing")
    return session


async def get_user_language(request: Request, accept_language: str = Header(default='uz', alias='Accept-Language')):
    if accept_language not in settings.LANGUAGES.keys():
        accept_language = translation.default
    with translation.use_locale(accept_language):
        request.state.language = accept_language
        yield


app_dependencies = [
    Depends(d)
    for d in
    [get_user_language, set_db]
]
