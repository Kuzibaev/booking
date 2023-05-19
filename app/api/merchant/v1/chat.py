from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import schemas, models
from app.api import deps
from app.crud import crud_chat
from app.models.enums import ChatSessionParticipant
from app.utils.paginator import Paginator, paginate

router = APIRouter()


@router.get('/topic/list/', response_model=List[schemas.ChatTopic],
            dependencies=[Depends(deps.get_current_user)], status_code=status.HTTP_200_OK)
async def get_merchant_topics(
        db: AsyncSession = Depends(deps.get_db),
):
    result = await crud_chat.get_merchant_chat_topics(db, )
    return result


@router.post("/session/create/")
async def create_merchant_session(
        data: schemas.ChatSessionCreate,
        db: AsyncSession = Depends(deps.get_db),
        user: models.MerchantUser = Depends(deps.get_current_user),
):
    chat_session, is_created = await crud_chat.create_merchant_chat_session(db, user.id, data.topic_id)

    if not is_created:
        ok, detail, status_code = False, 'There is an open session.', 400
    else:
        ok, detail, status_code = True, 'Chat session is created.', 201

    return JSONResponse({
        'ok': ok,
        'detail': detail,
        'session': jsonable_encoder(schemas.ChatSession.from_orm(chat_session))},
        status_code=status_code
    )


@router.get('/session/list/', response_model=schemas.DataResponse[schemas.ChatSession])
async def get_merchant_sessions(
        user: models.MerchantUser = Depends(deps.get_current_user),
        paginator: Paginator = Depends(paginate),
):
    return await paginator.execute(crud_chat.get_merchant_chat_sessions(user_id=user.id))


@router.put("/session/{session_id:int}/")
async def close_merchant_session(
        session_id: int,
        data: schemas.ChatSessionClose,
        db: AsyncSession = Depends(deps.get_db),
        user: models.MerchantUser = Depends(deps.get_current_user)
):
    is_changed = await crud_chat.close_merchant_chat_session(
        db=db,
        session_id=session_id,
        is_problem_resolved=data.is_problem_resolved,
        user_id=user.id,
    )
    if is_changed is None:
        response = JSONResponse({
            'ok': False,
            'detail': 'Chat session not found'
        }, status_code=404)
    elif is_changed is False:
        response = JSONResponse({
            'ok': False,
            'detail': "Couldn't update chat session",
        }, status_code=400)
    else:
        response = JSONResponse({
            'ok': True,
            'detail': 'Chat session is updated'
        })
    return response


@router.delete("/session/{session_id:int}/delete/")
async def delete_merchant_session(
        session_id: int,
        db: AsyncSession = Depends(deps.get_db),
        user: models.MerchantUser = Depends(deps.get_current_user)
):
    is_deleted = await crud_chat.delete_merchant_chat_session(db, session_id, user.id)
    if is_deleted:
        return JSONResponse({
            'ok': True,
            'detail': 'Chat session is deleted'
        })
    return JSONResponse({
        'ok': False,
        'detail': 'Chat session is not found',
    }, status_code=404)


@router.get('/message/list/', response_model=schemas.ChatSessionMessageList,
            dependencies=[Depends(deps.get_current_user)])
async def get_merchant_message(
        db: AsyncSession = Depends(deps.get_db),
        session_id: int = Query(alias="session"),
):
    return await crud_chat.get_merchant_session_messages(db=db, session_id=session_id)


@router.post('/message/create/', response_model=Optional[schemas.ChatMessage],
             dependencies=[Depends(deps.get_current_user)])
async def create_merchant_message(message_create: schemas.ChatMessageCreate, db: AsyncSession = Depends(deps.get_db)):
    return await crud_chat.create_merchant_message(
        db,
        session_id=message_create.session_id,
        message=message_create.message,
        from_whom=ChatSessionParticipant.USER,
    )


@router.delete('/message/{message_id:int}/delete/')
async def remove_merchant_message(
        message_id: int,
        db: AsyncSession = Depends(deps.get_db),
        user: models.MerchantUser = Depends(deps.get_current_user),
):
    is_deleted = await crud_chat.delete_merchant_chat_session(db, user_id=user.id, message_id=message_id)
    if is_deleted:
        return JSONResponse({'ok': True, 'detail': 'Message is deleted'}, status_code=200)
    return JSONResponse({'ok': True, 'detail': 'Can\'t delete the message'}, status_code=400)
