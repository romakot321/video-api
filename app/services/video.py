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
        return await self.video_repository.create(user_id=schema.user_id, app_bundle=schema.app_bundle)

    async def send(self, schema: VideoTaskCreateSchema, video_id: UUID) -> VideoTaskSchema | None:
        request = AITaskCreateRequestSchema(
            prompt=schema.prompt,
            image_url=schema.image_url,
            video_id=str(video_id)
        )

        logger.debug("Sending submit request to AI: " + str(request.model_dump()))
        response = await self.ai_repository.generate(request)
        if response is None:
            await self.video_repository.update(str(video_id), is_invalid=1, comment="Error when request sended")
            return
        logger.debug("Received response: " + str(response))

        return await self.video_repository.update(str(video_id), is_finished=0)

    async def get(self, video_id: UUID) -> VideoTaskSchema:
        return await self.video_repository.get(str(video_id))

    async def update(self, schema: AIVideoSchema, video_id: UUID):
        logger.debug("Receive webhook: " + str(schema.model_dump()))
        if schema.status == AITaskStatus.failed:
            await self.video_repository.update(str(video_id), is_invalid=1, comment=schema.error)
        if schema.status != AITaskStatus.succeeded:
            return
        await self.ai_repository.load_video(schema.output, str(video_id))
        await self.video_repository.update(str(video_id), is_finished=1)

    async def download(self, video_id: UUID) -> FileResponse:
        video = await self.video_repository.get(str(video_id))
        return FileResponse(self.ai_repository.make_video_file_path(str(video_id)))

    async def delete_expired(self):
        videos = await self.video_repository.list_expired()
        self.ai_repository.clean_videos([str(v.id) for v in videos])
        await self.video_repository.delete_expired()
        logger.info("Deleted " + str(len(videos)) + " expired videos")

