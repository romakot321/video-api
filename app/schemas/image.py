from pydantic import BaseModel, ConfigDict, computed_field
from uuid import UUID


class ImageSchema(BaseModel):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class ImageCreateSchema(BaseModel):
    user_id: str
    app_bundle: str

