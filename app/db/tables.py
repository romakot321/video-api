import datetime as dt
import uuid
from uuid import UUID
from enum import Enum

from sqlalchemy import bindparam
from sqlalchemy import CheckConstraint
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Table
from sqlalchemy import text
from sqlalchemy import UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped as M
from sqlalchemy.orm import mapped_column as column
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import false
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.associationproxy import AssociationProxy

from app.db.base import Base

sql_utcnow = text('(now() at time zone \'utc\')')


class BaseMixin:
    @declared_attr.directive
    def __tablename__(cls):
        letters = ['_' + i.lower() if i.isupper() else i for i in cls.__name__]
        return ''.join(letters).lstrip('_') + 's'

    created_at: M[dt.datetime] = column(server_default=sql_utcnow)
    updated_at: M[dt.datetime | None] = column(nullable=True, onupdate=sql_utcnow)
    id: M[UUID] = column(primary_key=True, index=True, default=uuid.uuid4)


class VideoStatus(Enum):
    finished = 'finished'
    queued = 'queued'
    error = 'error'


class Video(BaseMixin, Base):
    user_id: M[UUID] = column(primary_key=True, index=True)
    finished_at: M[dt.datetime | None] = column(nullable=True)
    status: M[VideoStatus] = column(default=VideoStatus.queued)
    comment: M[str | None] = column(nullable=True)
    app_bundle: M[str]


class Image(BaseMixin, Base):
    pass

