from fastapi import Request
from sqladmin import BaseView, expose, formatters
from sqladmin import ModelView
from sqladmin.helpers import slugify_class_name
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.core.sessions import database
from app.crud import crud_chat
from app.models.enums import ChatSessionParticipant


class Chat(BaseView):
    name = "Chat"
    template = "chat_messages.html"

    def is_visible(self, request: Request) -> bool:
        return False

    @expose('/chat/', identity='chat', methods=['GET', 'POST'])
    async def chat_user_list(self, request: Request):
        async with AsyncSession(database, expire_on_commit=False) as db:
            try:
                session_id = int(request.query_params.get('pk', None))
                session = await crud_chat.get_chat_session(db, session_id)
                if not session:
                    raise ValueError
            except (ValueError, TypeError):
                return self.templates.TemplateResponse(
                    '404.html',
                    context={'request': request}
                )

            if request.method == "POST":
                form_data = dict(await request.form())
                await crud_chat.create_message(
                    db,
                    session_id=session.id,
                    message=form_data.get('message'),
                    from_whom=ChatSessionParticipant.OPERATOR,
                )
            session_messages = await crud_chat.get_session_messages(db, session_id=session.id)
            response = self.templates.TemplateResponse(
                self.template,
                context={
                    'request': request,
                    'messages': session_messages.get("messages"),
                    'back_url': request.url_for(
                        "admin:list",
                        identity=slugify_class_name(ChatSession.__name__),
                    ),
                    'session': session
                }
            )
            return response


class ChatSession(ModelView, model=models.ChatSession):
    list_template = "chat_session_list.html"
    column_list = [
        "id",
        "user",
        "topic"
    ]
    form_columns = [
        'user',
        'topic',
        'status',
    ]

    def _url_for_reply(self, obj):
        return f"/admin/chat/?pk={obj.id}"


class ChatMessage(ModelView, model=models.ChatMessage):
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


class ChatTopic(ModelView, model=models.Topic):
    form_columns = [
        "title",
        "description",
    ]
    column_list = [
        'id',
        'title',
        'description'
    ]
