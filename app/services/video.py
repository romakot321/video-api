from fastapi import Depends, HTTPException
from fastapi.responses import FileResponse
from uuid import UUID
from loguru import logger
import asyncio

from app.repositories.ai import AIRepository
from app.repositories.video import VideoRepository
from app.schemas.video import VideoTaskCreateSchema, VideoTaskSchema
from app.schemas.ai import AITaskCreateRequestSchema
from app.schemas.ai import AIVideoSchema, AITaskStatus
from app.db.base import get_session


class VideoService:
    def __init__(
            self,
            ai_repository: AIRepository = Depends(),
            video_repository: VideoRepository = Depends()
    ):
        self.ai_repository = ai_repository
        self.video_repository = video_repository

    async def create(self, schema: VideoTaskCreateSchema) -> VideoTaskSchema:
        return await self.video_repository.create(user_id=schema.user_id)

    async def send(self, schema: VideoTaskCreateSchema, video_id: UUID) -> VideoTaskSchema:
        request = AITaskCreateRequestSchema(
            prompt=schema.prompt,
            video_id=str(video_id)
        )

        logger.debug("Sending submit request to AI: " + str(request.model_dump()))
        response = await self.ai_repository.generate(request)
        logger.debug("Received response: " + str(response))

        return await self.video_repository.update(str(video_id), is_finished=0)

    async def get(self, video_id: UUID) -> VideoTaskSchema:
        return await self.video_repository.get(str(video_id))

    async def update(self, schema: AIVideoSchema, video_id: UUID):
        logger.debug("Receive webhook: " + str(schema.model_dump()))
        if schema.status != AITaskStatus.succeeded:
            await self.video_repository.update(str(video_id), is_invalid=1)
            return
        await self.ai_repository.load_video(schema.output, str(video_id))
        await self.video_repository.update(str(video_id), is_finished=1)

    async def download(self, video_id: UUID) -> FileResponse:
        video = await self.video_repository.get(str(video_id))
        return FileResponse(self.ai_repository.make_video_file_path(str(video_id)))

