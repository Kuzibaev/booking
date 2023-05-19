from datetime import datetime

from pydantic import BaseModel, Field, Extra

from app.models.enums import Languages, BookingStatus
from app.schemas.property import PropertyEasy
from app.schemas.property_room import RoomTemplate
from app.schemas.user import User
from app.schemas.base import TranslatableModel, PhoneNumber
from app.schemas.docs import DocFile, Photo


class ReviewQuestionTranslationCreate(BaseModel):
    short_text: str
    text: str | None
    language: Languages
    is_default: bool = False


class ReviewQuestionCreate(BaseModel):
    short_text: str
    text: str | None
    translations: list[ReviewQuestionTranslationCreate] = []


class ReviewQuestion(TranslatableModel):
    id: int
    short_text: str
    text: str = None

    class Config:
        orm_mode = True


class ReviewQuestionAnswerCreate(BaseModel):
    question_id: int
    score: int = Field(ge=1, le=10)


class ReviewQuestionAnswer(ReviewQuestionAnswerCreate):
    question: ReviewQuestion
    created_at: datetime

    class Config:
        orm_mode = True


class PropertyReviewAnswer(ReviewQuestionAnswer):
    user: User | None = None
    comment: str | None = None


class ReviewAnswerCreate(BaseModel):
    property_id: int
    answers: list[ReviewQuestionAnswerCreate]
    comment: str | None

    class Config:
        extra = Extra.allow

    def get_score(self, question_id: int):
        for answer in self.answers:
            if answer.question_id == question_id:
                return answer.score
        return

    def get_score_avg(self, answers: list) -> float:
        total = 0
        for answer in answers:
            total += answer.score
        return total / len(answers)

    def validate_answers(self, questions: list[int]):
        questions = {q: 0 for q in questions}
        _exist_questions = []
        _not_exist_questions = []
        for answer in self.answers:
            if answer.question_id in questions:
                _exist_questions.append(answer.question_id)
                questions.pop(answer.question_id)
            else:
                _not_exist_questions.append(answer.question_id)
        if questions:
            raise ValueError(f"Not answered to {tuple(questions.keys())}")
        if _not_exist_questions:
            raise ValueError(f"Not exist questions {tuple(_not_exist_questions)}")


class ReviewAnonymousAnswerCreate(ReviewAnswerCreate):
    phone: PhoneNumber
    first_name: str
    last_name: str

    class Config:
        extra = Extra.allow


class UserReview(BaseModel):
    answers: list[ReviewQuestionAnswer]
    comment: str | None = ''


class PropertyReviewComment(BaseModel):
    id: int
    comment: str
    avg: float

    class Config:
        orm_mode = True


class Room(BaseModel):
    id: int
    room: RoomTemplate

    class Config:
        orm_mode = True


class PropertyReview(BaseModel):
    id: int
    name: str
    property: PropertyEasy
    booked_from: datetime
    booked_to: datetime
    status: BookingStatus
    reviews: list[ReviewQuestionAnswer] = []
    rooms: list[Room] = []
    comment: PropertyReviewComment | None = None

    class Config:
        orm_mode = True


class CommentUser(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    phone: str
    photo: Photo | None = None

    class Config:
        orm_mode = True


class CommentBooking(BaseModel):
    id: int
    booked_from: datetime
    booked_to: datetime

    class Config:
        orm_mode = True


class UserComment(BaseModel):
    id: int
    comment: str | None = None
    user: CommentUser | None = None
    booking: CommentBooking | None = None
    avg: float

    class Config:
        orm_mode = True


class QrCode(DocFile):
    pass


class PropertyQrCode(BaseModel):
    id: int | None
    property_id: int | None
    photo: QrCode | None

    class Config:
        orm_mode = True


class PropertyRatingItem(BaseModel):
    question: ReviewQuestion | None
    avg: float

    class Config:
        orm_mode = True
