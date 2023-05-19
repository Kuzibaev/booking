from .about_us import (
    AboutUs,
    Faq,
    FaqCreate,
    FaqUpdate
)
from .article import (
    ArticleCreate,
    Article,
    ArticleResponse
)
from .base import (
    DataResponse,
    OrdersResponse,
    BookingsResponse
)
from .booking import (
    Booking,
    BookingCreate,
    BookedRoom,
    BookedRoomCreate,
    BookingHistory,
    BookingUpdate,
    BookingReview,
    AcceptOrderWithRoom,
    PropertyHistoryOfBookings,
)
from .chat import (
    ChatMessage,
    ChatMessageCreate,
    ChatMessageDelete,
    ChatMessageTranslationCreate,
    ChatTopic,
    ChatSession,
    ChatSessionMessageList,
    ChatSessionCreate,
    ChatSessionClose
)
from .city import (
    City,
    CitySearch,
    CityCreate,
    CityTranslationCreate
)
from .contract import (
    Contract,
    ContractCreateOrUpdate
)
from .docs import (
    DocFile,
    DocFileCreate,
    DocFileUpdate
)
from .docs import (
    Photo,
    PhotoCreate
)
from .favourite import (
    UserFavouriteProperties,
    UserFavourite
)
from .login import (
    Login,
    LoginTokenResponse,
)
from .merchant_user import (
    MerchantUser,
    PersonalUser,
    MerchantUserUpdate,
    PersonalUserCreate,
    PersonalUserUpdate,
    MerchantUserResetPassword
)
from .property import (
    PropertyType,
    Property,
    PropertyEasy,
    PropertyUpdate,
    PropertySearch,
    PropertyRating,
    PropertyCreate,
    SavedFilter,
    PropertyReviewComment,
    PropertyPhoto,

    Language,
    BaseRoomType,
    PropertySettings,
    PropertySettingsUpdate,

)
from .property_room import (
    RoomTemplate,
    RoomTemplateWithRooms,
    RoomTemplateCreate,
    RoomTemplateUpdate,
    RoomNumberUpdate,
    RoomStatusUpdate,
    RoomBedCreate,
    RoomBedUpdate,
    Room,
    BedType,
    RoomTemplateBed,
    RoomStatus,
    RoomStatusByDay
)
from .reviews import (
    ReviewQuestion,
    PropertyReview,
    ReviewQuestionCreate,
    ReviewAnswerCreate,
    UserReview,
    ReviewQuestionAnswer,
    UserComment,
    PropertyRatingItem,
    ReviewAnonymousAnswerCreate,
)
from .service import (
    ServiceCategory,
    Service,
)
from .transaction import Transaction
from .user import (
    User,
    UserCreate,
    UserUpdate
)

for _entity in tuple(globals().values()):
    if hasattr(_entity, 'update_forward_refs'):
        _entity.update_forward_refs()
