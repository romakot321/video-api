from uuid import UUID
from fastapi import Depends, UploadFile
from pathlib import Path
import os

from fastapi.responses import FileResponse

from app.repositories.image import ImageRepository
from app.schemas.image import ImageSchema, ImageCreateSchema


class ImageService:
    image_directory = Path(os.getenv("IMAGE_DIRECTORY", 'image'))

    def __init__(self, image_repository: ImageRepository = Depends()):
        self.image_repository = image_repository

    @classmethod
    def _save_file(cls, body: bytes, filename: str):
        with open(cls.image_directory / filename, 'wb') as f:
            f.write(body)

    async def store_image(self, image: UploadFile) -> ImageSchema:
        model = await self.image_repository.create()
        self._save_file(image.file.read(), str(model.id))
        return model

    async def download_image(self, image_id: UUID) -> FileResponse:
        return FileResponse(self.image_directory / str(image_id))

