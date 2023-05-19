from io import BytesIO

import qrcode
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import operators
from starlette.responses import Response

from app import models
from app.core.conf import settings
from app.core.dependencies import get_db
from app.models import enums
from app.schemas import ReviewAnswerCreate
from app.schemas import reviews as schemas


async def get_review_questions(property_id: int, only_ids: bool = False):
    db = get_db()
    if only_ids:
        query = sa.select(models.PropertyReviewQuestion.id)
    else:
        query = sa.select(models.PropertyReviewQuestion)
    questions = (await db.execute(query.where(
        models.PropertyReviewQuestion.property_id == property_id
    ))).scalars().all()
    if not questions:
        questions = (await db.execute(query.where(
            operators.is_(models.PropertyReviewQuestion.property_id, None)
        ))).scalars().all()
    return questions


async def _create_or_update_comment(
        comment: str,
        user_id: int,
        property_id: int,
        avg: float,
        booking_id: int
):
    db = get_db()
    query = sa.select(models.UserComment).where(
        models.UserComment.user_id == user_id,
        models.UserComment.property_id == property_id,
        models.UserComment.booking_id == booking_id
    )
    user_comment: models.UserComment | None = (await db.execute(query)).scalar_one_or_none()
    if not user_comment:
        user_comment = models.UserComment(
            user_id=user_id,
            property_id=property_id,
            comment=comment,
            avg=avg,
            booking_id=booking_id
        )
        db.add(user_comment)
        await db.commit()
    else:
        user_comment.comment = comment
        user_comment.avg = avg
        user_comment.is_confirmed = False
        db.add(user_comment)
        await db.commit()


async def create_or_update_review(obj_in: ReviewAnswerCreate, user_id: int, avg: float, booking_id: int):
    db = get_db()
    await _create_or_update_comment(
        obj_in.comment,
        user_id=user_id,
        property_id=obj_in.property_id,
        avg=avg,
        booking_id=booking_id
    )
    existing_review_questions = (
        await db.execute(
            sa.select(models.ReviewQuestionAnswer).where(
                models.ReviewQuestionAnswer.user_id == user_id,
                models.ReviewQuestionAnswer.property_id == obj_in.property_id,
                models.ReviewQuestionAnswer.booking_id == booking_id
            )
        )
    ).scalars().all()
    question_ids_to_update = list(review.question_id for review in existing_review_questions)
    if existing_review_questions:
        update_stmt = (
            sa.update(
                models.ReviewQuestionAnswer
            ).where(
                models.ReviewQuestionAnswer.user_id == user_id,
                models.ReviewQuestionAnswer.property_id == obj_in.property_id,
                models.ReviewQuestionAnswer.booking_id == booking_id,
                models.ReviewQuestionAnswer.question_id == sa.bindparam('b_question_id'),
            ).values(
                score=sa.bindparam('b_score')
            )
        )
        params = [
            {
                'b_question_id': answer.question_id,
                'b_score': answer.score,
                'property_id': obj_in.property_id,
                'is_confirmed': False,
            } for answer in obj_in.answers if answer.question_id in question_ids_to_update
        ]
        await db.execute(
            update_stmt,
            params
        )
        await db.commit()
    answers_to_create = [
        {
            **answer.dict(),
            'booking_id': booking_id,
            'user_id': user_id,
            'property_id': obj_in.property_id
        } for answer in obj_in.answers if
        answer.question_id not in question_ids_to_update
    ]
    if answers_to_create:
        await db.execute(
            sa.insert(models.ReviewQuestionAnswer),
            answers_to_create
        )
        await db.commit()


def get_reviews_by_property_id(property_id: int):
    subquery = (
        sa.select(models.ReviewQuestionAnswer.booking_id)
        .where(models.Booking.id == models.ReviewQuestionAnswer.booking_id)
        .correlate(models.Booking)
        .exists()
    )

    query = (
        sa.select(models.Booking)
        .where(models.Booking.property_id == property_id)
        .where(models.Booking.status == enums.BookingStatus.CLOSED)
        .where(subquery)
    )

    return query.order_by(models.Booking.created_at.desc())


async def get_user_review(user_id: int, property_id: int, booking_id: int):
    db = get_db()
    answers_query = sa.select(models.ReviewQuestionAnswer).where(
        models.ReviewQuestionAnswer.user_id == user_id,
        models.ReviewQuestionAnswer.property_id == property_id,
        models.ReviewQuestionAnswer.booking_id == booking_id
    )
    answers = (await db.execute(answers_query)).scalars().all()
    comment_query = sa.select(models.UserComment.comment).where(
        models.UserComment.user_id == user_id,
        models.UserComment.property_id == property_id,
        models.UserComment.booking_id == booking_id,
    )
    comment = (await db.execute(comment_query)).scalars().first()
    return {
        'answers': answers,
        'comment': comment
    }


async def get_property_ratings(property_id: int) -> list[schemas.PropertyRatingItem]:
    db = get_db()
    query = sa.select(models.PropertyRatingItem).join(
        models.PropertyRating, models.PropertyRatingItem.rating_id == models.PropertyRating.id
    ).join(
        models.Property, models.PropertyRating.property_id == models.Property.id
    ).where(
        models.Property.id == property_id
    )

    property_ratings_items = (await db.execute(query)).scalars().unique().all()
    if property_ratings_items:
        return property_ratings_items
    return await make_get_property_reviews(property_id)


async def make_get_property_reviews(property_id):
    property_ratings_items = []
    questions = await get_review_questions(property_id)
    for q in questions:
        rating_item = schemas.PropertyRatingItem(avg=0, question=q)
        property_ratings_items.append(rating_item)
    return property_ratings_items


def get_property_comments(property_id: int):
    query = sa.select(models.UserComment).where(
        models.UserComment.property_id == property_id,
        models.UserComment.is_confirmed == True
    )
    return query


async def create_anonymous_review(db: AsyncSession, obj_in: schemas.ReviewAnonymousAnswerCreate, avg: float):
    user_comment = models.UserComment(property_id=obj_in.property_id, comment=obj_in.comment, avg=avg)

    answers_to_create = [
        {
            **answer.dict(),
            'property_id': obj_in.property_id,
            'is_confirmed': False,
        } for answer in obj_in.answers if
        answer.question_id
    ]
    if await db.execute(
            sa.insert(models.ReviewQuestionAnswer),
            answers_to_create
    ) and user_comment:
        db.add(user_comment)
        await db.commit()


async def create_qr_code(property_id: int):
    data = settings.QR_CODE_URL.format(f'{property_id}')  # Declaring the Variables

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, "PNG")
    buffer.seek(0)
    return Response(content=buffer.read(), media_type="image/png")
