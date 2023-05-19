import os
import random
import re
import string
import uuid
from pathlib import Path

import aiofiles
from aiofiles import ospath
from fastapi import UploadFile

from app.core.conf import settings

_IMAGE_EXTENSIONS = ['blp', 'bmp', 'dib', 'bufr', 'cur', 'pcx', 'dcx', 'dds', 'ps', 'eps', 'fit', 'fits', 'fli', 'flc',
                     'ftc', 'ftu', 'gbr', 'gif', 'grib', 'h5', 'hdf', 'png', 'apng', 'jp2', 'j2k', 'jpc', 'jpf', 'jpx',
                     'j2c', 'icns', 'ico', 'im', 'iim', 'tif', 'tiff', 'jfif', 'jpe', 'jpg', 'jpeg', 'mpg', 'mpeg',
                     'mpo', 'msp', 'palm', 'pcd', 'pdf', 'pxr', 'pbm', 'pgm', 'ppm', 'pnm', 'psd', 'bw', 'rgb', 'rgba',
                     'sgi', 'ras', 'tga', 'icb', 'vda', 'vst', 'webp', 'wmf', 'emf', 'xbm', 'xpm']

OS_OPEN_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)


def get_valid_filename(name):
    s = re.sub(r"(?u)[^-\w.]", "", str(name).strip().replace(" ", "_"))
    if s in {"", ".", ".."}:
        s = ''.join(random.choices(string.ascii_letters, k=20))
    file_name, ext = s.rsplit('.', 1)
    return file_name + (('.' + ext) if ext else '')


def get_available_filename(name: str):
    file_name, ext = name.rsplit('.', 1)
    return file_name + '_' + ''.join(random.choices(string.ascii_letters, k=20)) + (('.' + ext) if ext else '')


def get_available_image_extensions():
    return _IMAGE_EXTENSIONS


def validate_image_file_extension(value):
    return value in _IMAGE_EXTENSIONS


async def save_file(file: UploadFile | Path, override: bool = False, file_path: str = None,
                    is_auto_populate: bool = False):
    file_path = settings.MEDIA_ROOT / (file_path or settings.get_file_path())
    if not file_path.exists():
        Path.mkdir(file_path, parents=True)
    if is_auto_populate:
        _file_name = file.filename if isinstance(file, UploadFile) else file.name
    else:
        _file_name = file.filename
    file_name = get_valid_filename(_file_name)
    if override is False:
        while True:
            new_file_name = f"{str(uuid.uuid4())}_{file_name}"
            if not await ospath.exists(file_path / new_file_name):
                file_name = new_file_name
                break
    else:
        file_name = f"{str(uuid.uuid4())}_{file_name}"
    full_path = file_path / file_name
    try:
        if isinstance(file, Path):
            file = await aiofiles.open(file, 'rb')
        async with aiofiles.open(full_path, "wb") as out_file:
            while True:
                if chunk := await file.read(1024 * 64):
                    await out_file.write(chunk)
                else:
                    break
        return file_name
    finally:
        await file.close()
