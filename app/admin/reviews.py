from sqladmin import ModelView

from app import models


class PropertyRating(ModelView, model=models.PropertyRating):
    column_list = [
        'avg',
        'property'
    ]
    can_edit = False
    can_create = False
    can_delete = False
    can_export = False


class PropertyRatingItem(ModelView, model=models.PropertyRatingItem):
    column_list = [
        'id',
        'question',
        'rating',
        'avg',
    ]
    can_edit = False
    can_create = False
    can_delete = False
    can_export = False


class PropertyReviewQuestion(ModelView, model=models.PropertyReviewQuestion):
    form_columns = [
        "short_text",
        "text",
        "property"
    ]
    column_list = [
        "id",
        *form_columns
    ]


class PropertyReviewQuestionTranslation(ModelView, model=models.PropertyReviewQuestionTranslation):
    form_columns = [
        'question',
        'short_text',
        'text'
    ]

    column_list = [
        'id',
        *form_columns,
        'language'
    ]


class ReviewQuestionAnswer(ModelView, model=models.ReviewQuestionAnswer):
    form_columns = [
        'question',
        'property',
        'is_confirmed',
        'score',
    ]
    column_list = [
        'id',
        'property',
        'booking_id',
        'question',
        'user',
        'score',
        'is_confirmed'
    ]

    can_create = False
    can_export = True
    column_default_sort = ('id', True)


class UserComment(ModelView, model=models.UserComment):
    form_columns = [
        'property',
        'is_confirmed',
        'avg',
    ]

    column_list = [
        'id',
        'user',
        'comment',
        'property',
        'is_confirmed',
        'booking_id',
        'avg',
    ]

    column_default_sort = ('id', True)
