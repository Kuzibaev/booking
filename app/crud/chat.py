import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import operators

from app import models
from app.core.dependencies import get_db
from app.models import enums


class ChatCRUD:
    @staticmethod
    def get_chat_sessions(user_id: int):
        return sa.select(models.ChatSession).where(
            models.ChatSession.user_id == user_id
        ).options(
            joinedload(models.ChatSession.topic)
        )

    @staticmethod
    def get_merchant_chat_sessions(user_id: int):
        return sa.select(models.MerchantChatSession).where(
            models.MerchantChatSession.user_id == user_id
        ).options(
            joinedload(models.MerchantChatSession.topic)
        )

    @staticmethod
    async def create_chat_session(user_id: int, topic_id: int):
        db = get_db()
        stmt = sa.select(models.ChatSession).where(
            models.ChatSession.user_id == user_id,
            models.ChatSession.status == enums.ChatSessionStatus.OPEN,
            models.ChatSession.topic_id == topic_id
        )
        if session := (await db.execute(stmt)).scalar_one_or_none():
            return session, False
        new_session = models.ChatSession(
            user_id=user_id,
            topic_id=topic_id
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return new_session, True

    @staticmethod
    async def create_merchant_chat_session(db: AsyncSession, user_id: int, topic_id: int):
        stmt = sa.select(models.MerchantChatSession).where(
            models.MerchantChatSession.user_id == user_id,
            models.MerchantChatSession.status == enums.ChatSessionStatus.OPEN,
            models.MerchantChatSession.topic_id == topic_id
        )
        if session := (await db.execute(stmt)).scalar_one_or_none():
            return session, False
        new_session = models.MerchantChatSession(
            user_id=user_id,
            topic_id=topic_id
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)
        return new_session, True

    @staticmethod
    async def close_chat_session(db: AsyncSession, session_id: int, is_problem_resolved: bool, user_id: int = None):
        stmt = sa.select(
            models.ChatSession
        ).where(
            models.ChatSession.id == session_id
        )
        if user_id:
            stmt = stmt.where(
                models.ChatSession.user_id == user_id
            )
        chat_session: models.ChatSession = (await db.execute(stmt)).scalar_one_or_none()
        if not chat_session:
            return None

        if user_id:
            if chat_session.status == enums.ChatSessionStatus.CLOSED:
                chat_session.is_problem_resolved = is_problem_resolved
                await db.commit()
                return True
        else:
            if chat_session.status == enums.ChatSessionStatus.OPEN:
                chat_session.status = enums.ChatSessionStatus.CLOSED
                await db.commit()
                return True
        return False

    @staticmethod
    async def close_merchant_chat_session(db: AsyncSession, session_id: int, is_problem_resolved: bool,
                                          user_id: int = None):
        stmt = sa.select(
            models.MerchantChatSession
        ).where(
            models.MerchantChatSession.id == session_id
        )
        if user_id:
            stmt = stmt.where(
                models.MerchantChatSession.user_id == user_id
            )
        chat_session: models.MerchantChatSession = (await db.execute(stmt)).scalar_one_or_none()
        if not chat_session:
            return None

        if user_id:
            if chat_session.status == enums.ChatSessionStatus.CLOSED:
                chat_session.is_problem_resolved = is_problem_resolved
                await db.commit()
                return True
        else:
            if chat_session.status == enums.ChatSessionStatus.OPEN:
                chat_session.status = enums.ChatSessionStatus.CLOSED
                await db.commit()
                return True
        return False

    @staticmethod
    async def delete_chat_session(session_id: int, user_id: int):
        db = get_db()
        stmt = sa.select(models.ChatSession).where(
            models.ChatSession.user_id == user_id,
            models.ChatSession.id == session_id
        )
        chat_session = (await db.execute(stmt)).scalar_one_or_none()
        if chat_session:
            await db.delete(chat_session)
            await db.commit()
            return True

    @staticmethod
    async def delete_merchant_chat_session(db: AsyncSession, session_id: int, user_id: int):
        stmt = sa.select(models.MerchantChatSession).where(
            models.MerchantChatSession.user_id == user_id,
            models.MerchantChatSession.id == session_id
        )
        chat_session = (await db.execute(stmt)).scalar_one_or_none()
        if chat_session:
            await db.delete(chat_session)
            await db.commit()
            return True

    @staticmethod
    async def get_chat_session(db: AsyncSession, session_id: int):
        stmt = sa.select(models.ChatSession).where(
            models.ChatSession.id == session_id
        ).options(
            joinedload(models.ChatSession.user)
        ).options(
            joinedload(models.ChatSession.topic)
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    @staticmethod
    async def get_merchant_chat_session(db: AsyncSession, session_id: int):
        stmt = sa.select(models.MerchantChatSession).where(
            models.MerchantChatSession.id == session_id
        ).options(
            joinedload(models.MerchantChatSession.user)
        ).options(
            joinedload(models.MerchantChatSession.topic)
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    async def get_session_messages(self, db: AsyncSession, session_id: int,
                                   for_who: enums.ChatSessionParticipant = enums.ChatSessionParticipant.OPERATOR):
        chat_session = (
            await db.execute(
                sa.select(models.ChatSession).where(models.ChatSession.id == session_id))
        ).scalar_one_or_none()
        stmt = sa.select(models.ChatMessage).where(
            models.ChatMessage.session_id == session_id,
            operators.is_not(models.ChatMessage.is_deleted, True)
        ).order_by(
            sa.asc(models.ChatMessage.id)
        )
        messages: list[models.ChatMessage] = (await db.execute(stmt)).scalars().fetchall() or []
        await self.mark_messages_as_seen(db, messages=[m.id for m in messages if m.from_whom != for_who])
        return dict(session=chat_session, messages=messages)

    async def get_merchant_session_messages(
            self, db: AsyncSession,
            session_id: int,
            for_who: enums.ChatSessionParticipant = enums.ChatSessionParticipant.OPERATOR
    ):
        chat_session = (
            await db.execute(
                sa.select(models.MerchantChatSession).where(models.MerchantChatSession.id == session_id))
        ).scalar_one_or_none()
        stmt = sa.select(models.MerchantChatMessage).where(
            models.MerchantChatMessage.session_id == session_id,
            operators.is_not(models.MerchantChatMessage.is_deleted, True)
        ).order_by(
            sa.asc(models.MerchantChatMessage.id)
        )
        messages: list[models.MerchantChatMessage] = (await db.execute(stmt)).scalars().fetchall() or []
        await self.mark_merchant_messages_as_seen(db, messages=[m.id for m in messages if m.from_whom != for_who])
        return dict(session=chat_session, messages=messages)

    @staticmethod
    async def create_message(db: AsyncSession, session_id: int, message: str, from_whom: enums.ChatSessionParticipant):
        instance = models.ChatMessage(
            message=message,
            session_id=session_id,
            from_whom=from_whom
        )
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    async def create_merchant_message(db: AsyncSession, session_id: int, message: str,
                                      from_whom: enums.ChatSessionParticipant):
        instance = models.MerchantChatMessage(
            message=message,
            session_id=session_id,
            from_whom=from_whom
        )
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    @staticmethod
    def get_chat_topics():
        return sa.select(models.Topic).order_by(models.Topic.id)

    @staticmethod
    async def get_merchant_chat_topics(db: AsyncSession):
        stmt = sa.select(models.MerchantTopic).order_by(models.MerchantTopic.id)
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def delete_message(user_id: int, message_id: int):
        db = get_db()
        message: models.ChatMessage | None = (await db.execute(
            sa.select(models.ChatMessage).options(joinedload(models.ChatMessage.session)).where(
                models.ChatMessage.id == message_id))).scalar_one_or_none()
        if message and message.session.user_id == user_id:
            await db.delete(message)
            await db.commit()
            return True
        return False

    @staticmethod
    async def mark_messages_as_seen(db: AsyncSession, messages: list[int]):
        stmt = sa.update(models.ChatMessage).where(
            operators.is_(models.ChatMessage.is_seen, False),
            operators.in_op(models.ChatMessage.id, messages)
        ).values(
            is_seen=True
        ).execution_options(
            synchronize_session=False
        )
        await db.execute(stmt)
        await db.commit()

    @staticmethod
    async def mark_merchant_messages_as_seen(db: AsyncSession, messages: list[int]):
        stmt = sa.update(models.MerchantChatMessage).where(
            operators.is_(models.MerchantChatMessage.is_seen, False),
            operators.in_op(models.MerchantChatMessage.id, messages)
        ).values(
            is_seen=True
        ).execution_options(
            synchronize_session=False
        )
        await db.execute(stmt)
        await db.commit()


crud_chat = ChatCRUD()
