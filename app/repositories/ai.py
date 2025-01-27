import os
import hashlib
import asyncio
import aiohttp
from pydantic import ValidationError
from loguru import logger
from uuid import uuid4
import replicate

from app.schemas.ai import AITaskCreateRequestSchema
from app.schemas.ai import AIVideoSchema
from app.schemas.video import VideoTaskSchema


class AIRepository:
    token = os.getenv("REPLICATE_API_TOKEN")
    webhook_url = os.getenv("REPLICATE_API_WEBHOOK_URL").rstrip('/')
    video_directory = os.getenv("VIDEO_DIRECTORY", 'video').rstrip('/')

    async def generate(self, schema: AITaskCreateRequestSchema):
        try:
            return await replicate.predictions.async_create(
                model="luma/ray",
                input={"prompt": schema.prompt},
                webhook=self.webhook_url + "/" + schema.video_id,
                webhook_events_filter=["completed"]
            )
        except replicate.exceptions.ReplicateError as e:
            logger.exception(e)
            return None

    async def load_video(self, api_url: str, video_id: str):
        async with aiohttp.ClientSession() as session:
            file_response = await session.get(
                api_url,
                headers={"Authorization": "Bearer " + self.token}
            )
            assert file_response.status == 200, await file_response.text()
            with open(self.make_video_file_path(video_id), 'wb') as f:
                async for chunk in file_response.content.iter_chunked(1024):
                    f.write(chunk)

    @classmethod
    def clean_videos(cls, video_ids: list[str]):
        for i in video_ids:
            path = cls.make_video_file_path(i)
            try:
                os.remove(path)
            except FileNotFoundError:
                continue

    @classmethod
    def make_video_file_path(cls, video_id: str) -> str:
        return f'{cls.video_directory}/{video_id}.mp4'

