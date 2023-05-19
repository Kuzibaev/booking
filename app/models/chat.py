import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship

from .base import Base, TranslationBase
from .enums import ChatSessionParticipant, ChatSessionStatus


class Topic(Base):
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)

    translations = relationship("TopicTranslation", back_populates="topic", lazy='noload')
    sessions = relationship("ChatSession", back_populates="topic", lazy="noload")

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()


class MerchantTopic(Base):
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)

    translations = relationship("MerchantTopicTranslation", back_populates="topic", lazy='noload')
    sessions = relationship("MerchantChatSession", back_populates="topic", lazy="noload")

    def __str__(self):
        return self.title

    def __repr__(self):
        return self.__str__()


class ChatSession(Base):
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('user.id', ondelete='CASCADE'),
        nullable=False
    )
    user = relationship("User", lazy="noload")
    topic_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('topic.id', ondelete='SET NULL')
    )
    topic = relationship("Topic", back_populates="sessions", lazy="noload")
    status = sa.Column(ENUM(ChatSessionStatus), default=ChatSessionStatus.OPEN, nullable=False)
    has_new_message = sa.Column(sa.Boolean, default=False)
    last_message_from = sa.Column(ENUM(ChatSessionParticipant), nullable=True)
    is_problem_resolved = sa.Column(sa.Boolean, nullable=True)


class MerchantChatSession(Base):
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('merchant_user.id', ondelete='CASCADE'),
        nullable=False
    )
    user = relationship("MerchantUser", lazy="noload")
    topic_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('merchant_topic.id', ondelete='SET NULL')
    )
    topic = relationship("MerchantTopic", back_populates="sessions", lazy="noload")
    status = sa.Column(ENUM(ChatSessionStatus), default=ChatSessionStatus.OPEN, nullable=False)
    has_new_message = sa.Column(sa.Boolean, default=False)
    last_message_from = sa.Column(ENUM(ChatSessionParticipant), nullable=True)
    is_problem_resolved = sa.Column(sa.Boolean, nullable=True)


class ChatMessage(Base):
    message = sa.Column(sa.String, nullable=False)
    session_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('chat_session.id', ondelete='CASCADE'),
        nullable=False
    )
    session = relationship("ChatSession", lazy="noload")
    from_whom = sa.Column(ENUM(ChatSessionParticipant), default=ChatSessionParticipant.USER)
    is_seen = sa.Column(sa.Boolean, default=False)
    is_deleted = sa.Column(sa.Boolean, default=False)


class MerchantChatMessage(Base):
    message = sa.Column(sa.String, nullable=False)
    session_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('merchant_chat_session.id', ondelete='CASCADE'),
        nullable=False
    )
    session = relationship("MerchantChatSession", lazy="noload")
    from_whom = sa.Column(ENUM(ChatSessionParticipant), default=ChatSessionParticipant.USER)
    is_seen = sa.Column(sa.Boolean, default=False)
    is_deleted = sa.Column(sa.Boolean, default=False)


class TopicTranslation(TranslationBase):
    topic_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('topic.id', ondelete='SET NULL'),
        nullable=False
    )
    topic = relationship("Topic", back_populates="translations", lazy="noload")
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)


class MerchantTopicTranslation(TranslationBase):
    topic_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('merchant_topic.id', ondelete='SET NULL'),
        nullable=False
    )
    topic = relationship("MerchantTopic", back_populates="translations", lazy="noload")
    title = sa.Column(sa.String, nullable=False)
    description = sa.Column(sa.String)
