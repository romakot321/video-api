from fastapi import Depends
from loguru import logger
from uuid import uuid4

from app.db.base import get_session
from app.schemas.video import VideoTaskSchema


class VideoRepository:
    def __init__(self, session=Depends(get_session)):
        self.session = session

    def _generate_id(self) -> str:
        return str(uuid4())

    async def create(self) -> VideoTaskSchema:
        data = {
            "id": self._generate_id(),
            "is_finished": 0,
            "is_invalid": 0,
            "video_url": ""
        }
        await self.session.hset(data["id"], mapping=data)
        return VideoTaskSchema(**data)

    async def update(self, schema: VideoTaskSchema):
        data = schema.model_dump()
        data["is_finished"] = int(data["is_finished"])
        data["is_invalid"] = int(data["is_invalid"])
        await self.session.hset(schema.id, mapping=data)

    async def get(self, video_id: str) -> VideoTaskSchema | None:
        data = await self.session.hgetall(video_id)
        if not data:
            return None
        return VideoTaskSchema.model_validate(data)

