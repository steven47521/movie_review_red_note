from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    year: int | None = Field(default=None, ge=1888, le=2100)
