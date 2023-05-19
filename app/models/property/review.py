import sqlalchemy as sa
from sqlalchemy import event
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import operators
import logging
from app.core.sessions import database
from app.models.base import Base, TranslationBase


class PropertyReviewQuestion(Base):
    short_text = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String)
    property = relationship("Property", back_populates="review_questions", lazy="noload")
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='SET NULL'),
        nullable=True
    )
    translations = relationship("PropertyReviewQuestionTranslation", back_populates="question", lazy="selectin")

    def __str__(self):
        return f'{self.short_text}'

    def __repr__(self):
        return self.__str__()


class ReviewQuestionAnswer(Base):
    question_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_review_question.id", ondelete='CASCADE'),
        nullable=False
    )
    question = relationship("PropertyReviewQuestion", lazy="selectin")
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='CASCADE'),
        nullable=False
    )
    property = relationship("Property", lazy="selectin")
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=True
    )
    booking_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("booking.id"),
        nullable=True
    )
    booking = relationship("Booking", back_populates="reviews", lazy="noload")
    user = relationship("User", lazy="noload")
    score = sa.Column(sa.Float, nullable=False)
    is_confirmed = sa.Column(sa.Boolean, default=False, nullable=True)


class UserComment(Base):
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("user.id", ondelete="CASCADE"),
        nullable=True
    )
    user = relationship("User", lazy="selectin")
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='CASCADE'),
        nullable=False
    )
    booking_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("booking.id"),
        nullable=True
    )
    property = relationship("Property", lazy="noload")
    comment = sa.Column(sa.String, nullable=False)
    booking = relationship("Booking", back_populates="comment", lazy='selectin')
    avg = sa.Column(sa.Float, nullable=True)
    is_confirmed = sa.Column(sa.Boolean, default=False, nullable=True)


class PropertyReviewQuestionTranslation(TranslationBase):
    question_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_review_question.id", ondelete='CASCADE'),
        nullable=False
    )
    question = relationship("PropertyReviewQuestion", back_populates="translations", lazy="joined")
    short_text = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String)


class PropertyRating(Base):
    avg = sa.Column(sa.Float, default=0)
    property_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property.id', ondelete='CASCADE'),
        nullable=False
    )
    property = relationship("Property", lazy="selectin")

    def __str__(self):
        return str(self.property)

    def __repr__(self):
        return self.__str__()


class PropertyRatingItem(Base):
    rating_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('property_rating.id', ondelete="CASCADE"),
        nullable=False
    )
    rating = relationship("PropertyRating", lazy="noload")
    question_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("property_review_question.id", ondelete="CASCADE"),
        nullable=False
    )
    question = relationship("PropertyReviewQuestion", lazy="selectin")
    avg = sa.Column(sa.Float, default=0, nullable=False)

    def __str__(self):
        return str(self.avg)

    def __repr__(self):
        return self.__str__()


# EVENT LISTENERS
def receive_after_execute(conn, clause_element, *args):
    if isinstance(clause_element, (sa.sql.Update, sa.sql.Delete,)):
        if clause_element.table.name == ReviewQuestionAnswer.__tablename__:
            record = args[1]
            review_question_answer_id, is_confirmed = record.get('review_question_answer_id'), record.get(
                'is_confirmed')
            if is_confirmed and review_question_answer_id:
                with Session(bind=conn) as session:
                    property_id = get_property_id(session, review_question_answer_id)
                if property_id:
                    update_or_create_property_rating(conn, property_id=property_id)


def get_property_id(session, review_question_answer_id: int) -> int:
    property_id = session.query(ReviewQuestionAnswer.property_id).filter_by(
        id=review_question_answer_id).one_or_none()
    return property_id[0]


def find_or_create_property_rating(session, property_id):
    property_rating = session.query(PropertyRating).filter_by(property_id=property_id).one_or_none()

    if not property_rating:
        property_rating = PropertyRating(property_id=property_id, avg=0)
        session.add(property_rating)
        session.flush()

        questions = property_reviews_questions(session, property_id)
        property_rating_items = [
            PropertyRatingItem(rating_id=property_rating.id, question_id=question.id, avg=0)
            for question in questions
        ]
        session.add_all(property_rating_items)
        session.flush()
    return property_rating


def calculate_property_rating(session, property_id, property_rating):
    length, total = session.query(
        sa.func.count(ReviewQuestionAnswer.id),
        sa.func.sum(ReviewQuestionAnswer.score)
    ).filter_by(
        property_id=property_id,
        is_confirmed=True
    ).one()

    avg = total / length
    property_rating.avg = avg
    session.flush()


def calculate_property_question_answers(session, property_id, property_rating):
    questions_avg = session.query(
        ReviewQuestionAnswer.question_id,
        sa.func.avg(ReviewQuestionAnswer.score)
    ).filter_by(
        property_id=property_id,
        is_confirmed=True
    ).group_by(
        ReviewQuestionAnswer.question_id
    ).order_by(
        ReviewQuestionAnswer.question_id
    ).all()

    for question_id, avg_score in questions_avg:
        property_rating_item = session.query(PropertyRatingItem).filter_by(
            rating_id=property_rating.id,
            question_id=question_id
        ).one()

        property_rating_item.avg = avg_score
        session.flush()


def property_reviews_questions(session, property_id, only_ids=True):
    query = session.query(PropertyReviewQuestion.id) if only_ids else session.query(PropertyReviewQuestion)
    questions = query.filter_by(property_id=property_id).all()

    if not questions:
        questions = query.filter(operators.is_(PropertyReviewQuestion.property_id, None)).all()

    return questions


def update_or_create_property_rating(conn, property_id=None):
    with Session(bind=conn) as session:
        property_rating = find_or_create_property_rating(session, property_id)

        calculate_property_rating(session, property_id, property_rating)
        calculate_property_question_answers(session, property_id, property_rating)

        logging.info("PropertyRating and RatingItems calculated")


event.listen(database.sync_engine, 'after_execute', receive_after_execute)
