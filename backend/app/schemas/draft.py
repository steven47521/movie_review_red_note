from pydantic import BaseModel, Field


class RegeneratePartRequest(BaseModel):
    part: str = Field(..., pattern="^(title|hooks|body|tags)$")


class ManualDraftPatchRequest(BaseModel):
    title: str | None = None
    hooks: list[str] | None = None
    body: str | None = None
    tags: list[str] | None = None
