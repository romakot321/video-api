from pydantic import BaseModel, HttpUrl, root_validator
from uuid import UUID


class VideoTaskSchema(BaseModel):
    id: str
    is_finished: bool
    is_invalid: bool = False
    video_url: HttpUrl | None = None

    @root_validator(pre=True)
    @classmethod
    def translate_empty_to_none(cls, values) -> HttpUrl | None:
        if not isinstance(values, dict):
            return {}
        video_url = values.get("video_url")
        if isinstance(video_url, str) and not video_url:
            values["video_url"] = None
        return values


class VideoTaskCreateSchema(BaseModel):
    prompt: str

