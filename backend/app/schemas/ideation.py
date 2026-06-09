from pydantic import BaseModel, Field


class SelectAngleRequest(BaseModel):
    angle_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(default="")


class SelectRouteRequest(BaseModel):
    route_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    outline: list[str] = Field(default_factory=list)
