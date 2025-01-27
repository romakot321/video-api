from fastapi import Depends
from loguru import logger
from uuid import uuid4
from sqlalchemy import select, delete
import datetime as dt

from app.db.base import get_session
from app.db.tables import Video, VideoStatus
from app.schemas.video import VideoTaskSchema
from app.repositories.base import BaseRepository


class VideoRepository(BaseRepository):
    base_table = Video

    async def create(self, user_id: str, app_bundle: str) -> VideoTaskSchema:
        model = Video(user_id=user_id, app_bundle=app_bundle)
        model = await self._create(model)
        return VideoTaskSchema.model_validate(model)

    async def update(self, video_id: str, **fields):
        data = {k: v for k, v in fields.items() if v is not None}

        if "is_invalid" in data and data.pop("is_invalid"):
            data['status'] = VideoStatus.error
        elif "is_finished" in data and data.pop("is_finished"):
            data['status'] = VideoStatus.finished

        return VideoTaskSchema.model_validate(await self._update(video_id, **data))

    async def get(self, video_id: str) -> VideoTaskSchema:
        model = await self._get_one(id=video_id)
        return VideoTaskSchema.model_validate(model)

    async def list_expired(self) -> list[VideoTaskSchema]:
        cut_off_date = dt.datetime.utcnow()
        cut_off_date -= dt.timedelta(days=7)
        query = select(self.base_table).where(self.base_table.created_at <= cut_off_date)
        models = await self.session.scalars(query)
        return [
            VideoTaskSchema.model_validate(model)
            for model in models
        ]

    async def delete_expired(self):
        query = delete(self.base_table).where(self.base_table.created_at <= cut_off_date)
        await self.session.execute(query)
        await self.commit()

