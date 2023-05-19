import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import JSONResponse

from app import schemas
from app.api import deps
from app.core.conf import settings
from app.crud import crud_doc
from app.utils.file import save_file

router = APIRouter()


@router.get('/{doc_file_id}/', response_model=schemas.DocFile)
async def get_file(doc_file_id: UUID):
    if file := await crud_doc.get(file_id=doc_file_id):
        return file
    return JSONResponse({'ok': False, 'detail': 'Not found'}, status_code=404)


@router.post('/upload/', response_model=schemas.DocFile)
async def upload_file(file: UploadFile = File(...)):
    try:
        file_name = await save_file(file)
        doc_obj = schemas.DocFileCreate(
            name=file_name,
            type=file.content_type,
            path=(settings.get_file_path() / file_name).as_posix(),
        )
        return await crud_doc.create(obj_in=doc_obj)
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(e), "result": "error"},
        )
