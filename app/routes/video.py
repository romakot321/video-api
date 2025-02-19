from fastapi import APIRouter, Depends, File, Request, Header, HTTPException, Response, UploadFile
from fastapi import BackgroundTasks
from fastapi.responses import FileResponse
from uuid import UUID
from loguru import logger
import os

from app.schemas.image import ImageCreateSchema
from app.schemas.video import VideoTaskSchema, VideoTaskCreateSchema
from app.schemas.ai import AIVideoSchema
from app.services.image import ImageService
from app.services.video import VideoService
from slowapi.util import get_remote_address
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/video", tags=["Video"])
valid_access_tokens = os.getenv("ACCESS_TOKEN", "123").split(',')
api_url = os.getenv("REPLICATE_API_WEBHOOK_URL").rstrip('/').rstrip("/video/webhook")


@router.post(
    '',
    response_model=VideoTaskSchema,
    description="""
        Endpoint for start a task for video generation.
        For do request you need to specify Access-Token header, ask me in telegram about it.
        image_url can ba url from this documentation for image download
    """
)
async def create_video_task(
        schema: VideoTaskCreateSchema,
        request: Request,
        background_tasks: BackgroundTasks,
        file: UploadFile | None = None,
        access_token: str = Header(),
        service: VideoService = Depends(),
        image_service: ImageService = Depends()
):
    if access_token not in valid_access_tokens:
        raise HTTPException(401)
    if file is not None:
        image = await image_service.store_image(file, ImageCreateSchema.model_validate(schema))
        schema.image_url = api_url + "/image/" + str(image.id)
    response = await service.create(schema)
    background_tasks.add_task(service.send, schema, response.id)
    return response


@router.get(
    '/{video_id}',
    response_model=VideoTaskSchema,
    description="""
        Endpoint for check the task of video generation status.
        For do request you need to specify Access-Token header, ask me in telegram about it.
    """
)
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
    await service.delete_expired()
    await service.update(schema, video_id)
    return 'OK'


@router.get(
    '/file/{video_id}',
    response_class=FileResponse,
    description="""
        Endpoint for download the file with generated video.
    """
)
async def download_video_file(
        video_id: UUID,
        request: Request,
        service: VideoService = Depends()
):
    return await service.download(video_id)

