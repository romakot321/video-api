from pydantic import BaseModel, HttpUrl, Field
from uuid import UUID
from enum import Enum


class AITaskCreateRequestSchema(BaseModel):
    prompt: str
    image_url: str | None = None
    video_id: str


class AITaskStatus(str, Enum):
    succeeded = 'succeeded'
    starting = 'starting'
    processing = 'processing'
    failed = 'failed'
    canceled = 'canceled'


class AIVideoSchema(BaseModel):
    id: str
    output: str | None = None
    status: AITaskStatus
    error: str | None = None

