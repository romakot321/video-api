from uuid import UUID
from fastapi import Depends, APIRouter, File, Header, UploadFile
import os

from fastapi.responses import FileResponse

from app.services.image import ImageService
from app.schemas.image import ImageSchema, ImageCreateSchema

router = APIRouter(prefix="/image", tags=["Image"])
valid_access_tokens = os.getenv("ACCESS_TOKEN", "123").split(',')


@router.post("", response_model=ImageSchema)
async def upload_image(
        access_token: str = Header(),
        file: UploadFile = File(),
        service: ImageService = Depends()
):
    if access_token not in valid_access_tokens:
        raise HTTPException(401)
    return await service.store_image(file)


@router.get("/{image_id}", response_class=FileResponse)
async def download_image(
        image_id: UUID,
        service: ImageService = Depends()
):
    return await service.download_image(image_id)

