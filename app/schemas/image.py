from pydantic import BaseModel, ConfigDict, computed_field
from uuid import UUID


class ImageSchema(BaseModel):
    id: UUID


class ImageCreateSchema(BaseModel):
    user_id: str
    app_bundle: str

