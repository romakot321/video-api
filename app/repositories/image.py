from fastapi import Depends
from loguru import logger
from uuid import uuid4
from sqlalchemy import select, delete
import datetime as dt

from app.db.base import get_session
from app.db.tables import Image
from app.schemas.image import ImageSchema, ImageCreateSchema
from app.repositories.base import BaseRepository


class ImageRepository(BaseRepository):
    base_table = Image

    async def create(self) -> ImageSchema:
        model = Image()
        model = await self._create(model)
        return ImageSchema.model_validate(model)

    async def get(self, image_id: str) -> ImageSchema:
        model = await self._get_one(id=image_id)
        return ImageSchema.model_validate(model)

    async def list_expired(self) -> list[ImageSchema]:
        cut_off_date = dt.datetime.utcnow()
        cut_off_date -= dt.timedelta(days=30)
        query = select(self.base_table).where(self.base_table.created_at <= cut_off_date)
        models = await self.session.scalars(query)
        return [
            ImageSchema.model_validate(model)
            for model in models
        ]

    async def delete_expired(self):
        cut_off_date = dt.datetime.utcnow()
        cut_off_date -= dt.timedelta(days=30)
        query = delete(self.base_table).where(self.base_table.created_at <= cut_off_date)
        await self.session.execute(query)
        await self.commit()
