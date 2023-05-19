from enum import Enum


class Languages(Enum):
    UZ = 'uz'
    RU = 'ru'
    EN = 'en'


class BillingUnit(str, Enum):
    FIXED_VALUE = 'fixed_value'
    PERCENTAGE_VALUE = 'percentage_value'


class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'


class ChatSessionParticipant(Enum):
    OPERATOR = 'operator'
    USER = 'user'


class ChatSessionStatus(Enum):
    OPEN = 'open'
    CLOSED = 'closed'


class PropertyStarRating(str, Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5


class PropertyStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    IN_ACTIVE = "in_active"


class PropertySortBy(Enum):
    NEWEST = 'newest'
    PRICE = 'price'
    DISCOUNT = 'discount'
    RATING = 'rating'


class SortType(Enum):
    DESC = 'desc'
    ASC = 'asc'


class StatusBy(Enum):
    CONFIRMED = "confirmed"
    ACTIVE = "active"


class CityCentreDistance(str, Enum):
    ONE_THREE = '1-3'
    FOUR_SIX = '4-6'
    SEVEN_PLUS = '7+'


class BookingStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    CLOSED = "closed"
    CANCELED = "canceled"


class MerchantUserRole(Enum):
    CHIEF = 'chief'
    MANAGER = 'manager'


class SocialType(Enum):
    FACEBOOK = "facebook"
    GOOGLE = "google"


class SearchType(Enum):
    ALL = 'all'
    NAME = 'name'
    # ROOM_NAME = 'room_name'
    PRICE = 'price'


class OrderStatus(Enum):
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    CANCELED = "canceled"


class OrderHistoryStatus(Enum):
    CLOSED = "closed"
    CANCELED = "canceled"


class AcceptOrCancel(Enum):
    ACCEPT = "accept"
    CANCEL = "cancel"


class CountByDays(Enum):
    LAST_30_DAYS = "last_30_days"
    LAST_15_DAYS = "last_15_days"
    LAST_WEEK = "last_week"
    YESTERDAY = "yesterday"
    TODAY = "today"


class HistorySortBy(Enum):
    ROOM_NAME = 'room_name'
    NAME = 'name'
    NUMBER_OF_PEOPLE = 'number_of_people'
    CHECKIN_AND_CHECKOUT = 'checkin_and_checkout'
    STATUS = 'status'
    PRICE = 'price'


class OrderSortBy(Enum):
    BY_PRICE = "by_price"
    BY_ROOM = "by_room"
    BY_DATE = "by_date"
    QTY_PEOPLE = "qty_people"


class TransactionTitle(Enum):
    FOR_SERVICE = 'for_service'
    TOP_UP_THE_BALANCE = 'top_up_the_balance'


class TransactionStatus(Enum):
    SUCCESS = 'success'
    ERROR = 'error'


class TransactionType(Enum):
    UZUM = 'uzum_uz'
    PAY_ME = 'pay_me_uz'
    CLICK = 'click_uz'
    CASH = 'cash'


class PaymentStatus(Enum):
    WAITING = "waiting"
    PREAUTH = "preauth"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    REFUNDED = "refunded"
    ERROR = "error"
    INPUT = "input"


class RoomStatus(Enum):
    EMPTY = 'empty'
    BUSY = 'busy'
    UNDER_RENOVATION = 'under_renovation'


class BookingCanceledBy(Enum):
    CLIENT = "client"
    MERCHANT_USER = "merchant_user"
