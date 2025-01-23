from fastapi import Depends
from loguru import logger
from uuid import uuid4

from app.db.base import get_session
from app.db.tables import Video, VideoStatus
from app.schemas.video import VideoTaskSchema
from app.repositories.base import BaseRepository


class VideoRepository(BaseRepository):
    base_table = Video

    async def create(self, user_id: str) -> VideoTaskSchema:
        model = Video(user_id=user_id)
        model = await self._create(model)
        return VideoTaskSchema.model_validate(model)

    async def update(self, schema: VideoTaskSchema):
        data = schema.model_dump(exclude_none=True)

        status = VideoStatus.queued
        if data.pop("is_invalid"):
            status = VideoStatus.error
        elif data.pop("is_finished"):
            status = VideoStatus.finished
        data['status'] = status

        return VideoTaskSchema.model_validate(await self._update(schema.id, **data))

    async def get(self, video_id: str) -> VideoTaskSchema:
        model = await self._get_one(id=video_id)
        return VideoTaskSchema.model_validate(model)

