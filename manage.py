import asyncio
import inspect
import logging
import os.path
from datetime import datetime
from functools import wraps
from typing import Generator, cast

import typer
from babel.messages.catalog import Catalog
from babel.messages.extract import extract_from_dir
from babel.messages.mofile import write_mo
from babel.messages.pofile import write_po, read_po
from babel.util import LOCALTZ
from click import Choice
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.conf import settings
from app.core.sessions import database
from app.main import app

typer_app = typer.Typer()

logger = logging.getLogger(__file__)


# @typer_app.command()
# def createsuperuser():
#     phone = typer.prompt('Enter phone number')
#     password = typer.prompt('Enter password', hide_input=True, confirmation_prompt="Enter password again")


@typer_app.command()
def runserver(reload: bool = True, port: int = 8000):
    import uvicorn
    uvicorn.run(
        'app.main:app',
        reload=reload,
        port=port,
        host='localhost',
        log_level='debug'
    )


@typer_app.command(name="makemessages")
def make_messages(
        all_: bool = typer.Option(False, '--all', '-a', help="Updates the message files for all available languages."),
        locale: str = typer.Option("", '--locale', '-l', help="Specifies the locale(s) to process.")
):
    if not os.path.exists('locales'):
        os.mkdir('locales')

    if (all_ is False and not locale) or (all_ and locale):
        locale = typer.prompt(
            'Enter a locale name',
            type=Choice(settings.LANGUAGES),
            show_choices=True
        )
    template = Catalog(
        project=settings.PROJECT_NAME,
        domain=settings.get_project_name(),
        last_translator='',
    )
    extracted = cast(Generator, extract_from_dir())
    for filename, lineno, message, comments, context in extracted:
        filepath = filename  # already normalized
        template.add(message, None, [(filepath, lineno)],
                     auto_comments=comments, context=context)
    domain = settings.get_project_name()
    languages = {locale: settings.LANGUAGES[locale]} if locale else settings.LANGUAGES
    for lang in languages:
        output_file = os.path.join(settings.LOCALES_DIR, lang, 'LC_MESSAGES', domain + '.po')
        if not os.path.exists(os.path.dirname(output_file)):
            os.makedirs(os.path.dirname(output_file))
        if not os.path.isfile(output_file):
            catalog = Catalog(
                project=settings.PROJECT_NAME,
                domain=domain,
                locale=lang,
                revision_date=datetime.now(LOCALTZ),
                fuzzy=False,
            )
            with open(output_file, 'wb') as file_obj:
                write_po(file_obj, catalog, 76)
        else:
            with open(output_file, 'rb') as old_po_file:
                catalog = read_po(old_po_file, locale=lang, domain=domain)

        with open(output_file, 'wb') as file_obj:
            catalog.update(template, False, update_header_comment=True)
            write_po(file_obj, catalog, width=76)
        text = typer.style(f'Locale {lang} processed', fg='green', bold=True)
        typer.echo(text, color=True)


@typer_app.command(name="compilemessages")
def compile_messages(
        statistics: bool = typer.Option(False, '--statistics', '-s'),
        use_fuzzy: bool = typer.Option(False, '--use-fuzzy', '-f')
):
    po_files = []
    mo_files = []
    directory = settings.LOCALES_DIR
    domain = settings.get_project_name()
    for locale in os.listdir(directory):
        po_file = os.path.join(directory, locale,
                               'LC_MESSAGES', domain + '.po')
        if os.path.exists(po_file):
            po_files.append([locale, po_file])
            mo_files.append(os.path.join(directory, locale,
                                         'LC_MESSAGES',
                                         domain + '.mo'))
    if not po_files:
        ex = typer.style('no message catalogs found', fg='red')
        typer.echo(ex)
        return

    catalogs_and_errors = {}

    for idx, (locale, po_file) in enumerate(po_files):
        mo_file = mo_files[idx]
        with open(po_file, 'rb') as infile:
            catalog = read_po(infile, locale)

        if statistics:
            translated = 0
            for message in list(catalog)[1:]:
                if message.string:
                    translated += 1
            percentage = 0
            if len(catalog):
                percentage = translated * 100 // len(catalog)
            typer.echo(
                typer.style(f'{translated} of {len(catalog)} messages '
                            f'({percentage}%) translated in {locale}.po',
                            fg='green')
            )

        if catalog.fuzzy and not use_fuzzy:
            typer.echo(f'catalog {po_file} is marked as fuzzy, skipping')
            continue

        catalogs_and_errors[catalog] = catalog_errors = list(catalog.check())
        for message, errors in catalog_errors:
            for error in errors:
                typer.echo(
                    typer.style(f'error: {po_file}:{message.lineno}: {error}',
                                fg='red')
                )

        typer.echo(
            typer.style(f'compiling file {locale}.po to {locale}.mo',
                        fg='green', bold=True)
        )

        with open(mo_file, 'wb') as outfile:
            write_mo(outfile, catalog, use_fuzzy=use_fuzzy)

    return catalogs_and_errors


async def run_coroutine_within_app(fn):
    try:
        for callback in app.router.on_startup:
            if inspect.iscoroutinefunction(callback):
                await callback()
            else:
                callback()
        await fn
    finally:
        for callback in app.router.on_shutdown:
            if inspect.iscoroutinefunction(callback):
                await callback()
            else:
                callback()


def coro(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        asyncio.run(run_coroutine_within_app(fn=f(*args, **kwargs)))

    return wrapper


@typer_app.command(name="auto_populate")
@coro
async def auto_populate_datas(test: bool = typer.Option(False, '--test', '-t'), ):
    from _auto_populate_datas import get_model_datas
    if test:
        typer.echo(typer.style(
            "[TEST]", fg='green', bold=True
        ))
    typer.echo(typer.style(
        "Finding models...", fg='green', bold=True
    ))
    model_datas = get_model_datas()
    typer.echo(
        typer.style(f'Models orders are resolved... Adding to database.',
                    fg='green', bold=True)
    )
    async with AsyncSession(database, expire_on_commit=False) as session:
        for model_data in model_datas:
            try:
                if test is False:
                    await model_data.save(session)
            except (DBAPIError, Exception) as e:
                logger.error(e)
                typer.echo(
                    typer.style(f'- {model_data.model.__name__} failed!\n'
                                f'{e}',
                                fg='red', bold=True)
                )
            else:
                typer.echo(
                    typer.style(f'- {model_data.model.__name__} done!',
                                fg='green', bold=True)
                )


if __name__ == '__main__':
    typer_app()
