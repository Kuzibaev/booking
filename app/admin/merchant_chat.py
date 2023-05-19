from fastapi import Request
from sqladmin import BaseView, expose
from sqladmin import ModelView
from sqladmin.helpers import slugify_class_name
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.sessions import database
from app.crud import crud_chat
from app.models.enums import ChatSessionParticipant


class MerchantChat(BaseView):
    name = "MerchantChat"
    template = "chat_messages.html"

    def is_visible(self, request: Request) -> bool:
        return False

    @expose('/merchant/chat/', identity='merchant-chat', methods=['GET', 'POST'])
    async def chat_merchant_user_list(self, request: Request):
        async with AsyncSession(database, expire_on_commit=False) as db:
            try:
                session_id = int(request.query_params.get('pk', None))
                session = await crud_chat.get_merchant_chat_session(db, session_id)
                if not session:
                    raise ValueError
            except (ValueError, TypeError):
                return self.templates.TemplateResponse(
                    '404.html',
                    context={'request': request}
                )

            if request.method == "POST":
                form_data = dict(await request.form())
                await crud_chat.create_merchant_message(
                    db,
                    session_id=session.id,
                    message=form_data.get('message'),
                    from_whom=ChatSessionParticipant.OPERATOR,
                )
            session_messages = await crud_chat.get_merchant_session_messages(db, session_id=session.id)
            response = self.templates.TemplateResponse(
                self.template,
                context={
                    'request': request,
                    'messages': session_messages.get("messages"),
                    'back_url': request.url_for(
                        "admin:list",
                        identity=slugify_class_name(MerchantChatSession.__name__),
                    ),
                    'session': session
                }
            )
            return response


class MerchantChatSession(ModelView, model=models.MerchantChatSession):
    list_template = "chat_session_list.html"

    column_list = [
        "id",
        "user",
        "topic",
    ]
    form_columns = [
        'user',
        'topic',
        'status',
    ]

    def _url_for_reply(self, obj):
        return f"/admin/merchant/chat/?pk={obj.id}"


class MerchantChatMessage(ModelView, model=models.MerchantChatMessage):
    form_columns = [
        "session",
        "message",
        "from_whom",
        "is_seen",
        "is_deleted",
    ]

    column_list = [
        'id',
        'message',
        'session_id',
        'is_seen',
        'is_deleted'
    ]


class MerchantChatTopic(ModelView, model=models.MerchantTopic):
    form_columns = [
        "title",
        "description",
    ]
    column_list = [
        'id',
        'title',
        'description'
    ]
