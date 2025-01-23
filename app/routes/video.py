from fastapi import APIRouter, Depends, Request, Header, HTTPException, Response
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
from uuid import UUID
import os

from app.schemas.video import VideoTaskSchema, VideoTaskCreateSchema
from app.schemas.ai import AIVideoSchema
from app.services.video import VideoService
from slowapi.util import get_remote_address
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/video", tags=["Video"])
valid_access_tokens = os.getenv("ACCESS_TOKEN", "123").split(',')


@router.post(
    '',
    response_model=VideoTaskSchema,
    description="""
        Endpoint for start a task for video generation.
        For do request you need to specify Access-Token header, ask me in telegram about it.

        This endpoint rate-limited to 5 requests per minute.
    """
)
@limiter.limit("5/minute")
async def create_video_task(
        schema: VideoTaskCreateSchema,
        request: Request,
        background_tasks: BackgroundTasks,
        access_token: str = Header(),
        service: VideoService = Depends()
):
    if access_token not in valid_access_tokens:
        raise HTTPException(401)
    response = await service.create(schema)
    background_tasks.add_task(service.send, schema, response.id)
    return response


@router.get(
    '/{video_id}',
    response_model=VideoTaskSchema,
    description="""
        Endpoint for check the task of video generation status.
        For do request you need to specify Access-Token header, ask me in telegram about it.

        This endpoint rate-limited to 10 requests per minute.
    """
)
@limiter.limit("10/minute")
async def get_video_task(
        video_id: UUID,
        request: Request,
        access_token: str = Header(),
        service: VideoService = Depends()
):
    if access_token not in valid_access_tokens:
        raise HTTPException(401)
    return await service.get(video_id)


@router.post(
    '/webhook/{video_id}',
    include_in_schema=False
)
async def ai_api_webhook(
        video_id: UUID,
        schema: AIVideoSchema,
        service: VideoService = Depends()
) -> str:
    await service.update(schema, video_id)
    return 'OK'


@router.get(
    '/file/{video_id}',
    response_class=FileResponse,
    description="""
        Endpoint for download the file with generated video.
        For do request you need to specify Access-Token header, ask me in telegram about it.
    """
)
async def download_video_file(
        video_id: UUID,
        request: Request,
        access_token: str = Header(),
        service: VideoService = Depends()
):
    if access_token not in valid_access_tokens:
        raise HTTPException(401)
    return await service.download(video_id)

