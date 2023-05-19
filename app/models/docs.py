import uuid
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.core.conf import settings
from .base import BaseClass


class DocFile(BaseClass):
    __tablename__ = 'doc_file'

    id = sa.Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name: str = sa.Column(sa.String, nullable=False)
    type: str = sa.Column(sa.String, nullable=False)
    path: str = sa.Column(sa.String, nullable=False)

    created_at = sa.Column(sa.DateTime, server_default=func.now())
    updated_at = sa.Column(sa.DateTime, onupdate=func.now())

    def __repr__(self):
        return 'DocFile id {}'.format(self.id)

    def file_path(self) -> str:
        return Path(settings.MEDIA_PATH, self.path).as_posix()

    def full_path(self) -> str:
        return settings.SITE_URL + self.file_path()

    @property
    def url(self):
        return self.full_path()

    def __str__(self):
        return self.path  # .rsplit('/', 1)[-1]
