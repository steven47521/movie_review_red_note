from pydantic import BaseModel, Field


class RegenerateImageRequest(BaseModel):
    image_id: str = Field(..., min_length=1)
    reason: str = Field(default="")
