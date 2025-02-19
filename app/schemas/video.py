from pydantic import BaseModel, ConfigDict, model_validator
from uuid import UUID
from enum import Enum


class VideoTaskSchema(BaseModel):
    id: UUID
    user_id: UUID
    is_finished: bool
    is_invalid: bool = False
    comment: str | None = None

    @model_validator(mode='before')
    @classmethod
    def translate_status(cls, state):
        if not isinstance(state, dict):
            state = state.__dict__
        if state.get('status') and isinstance(state["status"], Enum):
            state["is_finished"] = state["status"].value == "finished"
            state["is_invalid"] = state["status"].value == "error"
        return state

    model_config = ConfigDict(from_attributes=True)


class VideoTaskCreateSchema(BaseModel):
    prompt: str
    image_url: str | None = None
    user_id: UUID
    app_bundle: str

