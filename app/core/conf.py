import os
from datetime import datetime
from pathlib import Path
from typing import List, Any

import pytz
from eskiz_sms.async_ import EskizSMS
from pydantic import BaseSettings, AnyHttpUrl, validator, PostgresDsn

APP_DIR = Path(__file__).parent.parent
BASE_DIR = APP_DIR.parent
DEBUG = os.getenv('DEBUG', 'True') == 'True'


class Settings(BaseSettings):
    # Project Config
    PROJECT_NAME: str = "Think Booking"
    SITE_URL: str
    SECRET_KEY: str
    DEBUG: bool = DEBUG

    # Token Expire
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 20  # 20 days

    # Google
    GOOGLE_CLIENT_ID: str | None
    GOOGLE_SECRET_KEY: str | None
    GOOGLE_WEBHOOK_OAUTH_REDIRECT_URI: str | None

    # Facebook
    FACEBOOK_CLIENT_ID: str | None
    FACEBOOK_SECRET_KEY: str | None
    FACEBOOK_WEBHOOK_OAUTH_REDIRECT_URI: str | None

    # LinkedIn
    LINKEDIN_CLIENT_ID: str | None
    LINKEDIN_SECRET_KEY: str | None
    LINKEDIN_WEBHOOK_OAUTH_REDIRECT_URI: str | None

    # Apple
    APPLE_CLIENT_ID: str | None
    APPLE_SECRET_KEY: str | None
    APPLE_WEBHOOK_OAUTH_REDIRECT_URI: str | None

    # Redis
    REDIS_URL: str

    # QR code generate url
    QR_CODE_URL: str = None

    MERCHANT_PASS: str = None

    # DB Config
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int
    DB_CONFIG: str = ''

    # Eskiz Config
    ESKIZ_EMAIL: str
    ESKIZ_PASSWORD: str
    ESKIZ_SMS_TEXT: str = "Your confirmation: {code}"  # noqa

    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        'http://localhost:3000',
        'http://localhost:3001',
        'http://localhost:3002',
    ]

    # Timezone
    TIMEZONE: str = 'Asia/Tashkent'

    # Media Root
    LOCALES_DIR: Path | str = BASE_DIR / 'locales'
    MEDIA_ROOT: Path | str = BASE_DIR / 'cdn' / 'media'
    MEDIA_PATH: str = '/media/'
    FILE_PATH: str = "%Y/%m/%d"

    # Languages
    LANGUAGES: dict = {
        'uz': "O'zbek",
        'en': "English",
        'ru': "Русский",
    }

    RATE_LIMIT_PREFIX: str = 'app:rl:'
    CODE_LIFETIME: int = 300  # seconds

    # Debug Config
    DEBUG_SMS_CODE: str = '******'
    DEBUG_PHONE: str = "+998*********"

    @validator('DB_CONFIG')
    def db_config(cls, _, values: dict):
        return PostgresDsn.build(
            scheme='postgresql+asyncpg',
            user=values['DB_USER'],
            password=values['DB_PASSWORD'],
            host=values['DB_HOST'],
            port=str(values['DB_PORT']),
            path=f"/{values['DB_NAME']}"

        )

    @validator("QR_CODE_URL")
    def validate_qr_code_url(cls, _, ):
        return "https://somesite.uz/ru/hotel-review/{0}"

    def get_project_name(self):
        return self.PROJECT_NAME.lower().replace(' ', '_').replace("-", "_")

    def get_project_slug(self):
        return self.PROJECT_NAME.lower().replace(' ', '-').replace('_', '-')

    timezone: Any = pytz.timezone(TIMEZONE)

    @property
    def datetime(self) -> datetime:
        return datetime.now(self.timezone)

    def get_file_path(self, file_path: str = None):
        return Path(self.datetime.strftime(file_path or self.FILE_PATH))

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


settings = Settings()

eskiz = EskizSMS(
    email=settings.ESKIZ_EMAIL,
    password=settings.ESKIZ_PASSWORD,
    save_token=True,
    env_file_path='.env'
)
