from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse

from app.core.conf import settings

router = APIRouter(prefix='/media')


@router.get('/{file_path:path}/')
async def response_media_file(file_path: str):
    full_path = Path(settings.MEDIA_ROOT, file_path)
    if full_path.exists():
        return FileResponse(full_path)
    return JSONResponse({'ok': False, 'detail': 'Not found'}, status_code=404)
