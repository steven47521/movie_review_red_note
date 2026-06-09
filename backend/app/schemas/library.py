from pydantic import BaseModel


class UpdateSessionFlagsRequest(BaseModel):
    is_favorite: bool | None = None
    is_published: bool | None = None


class SessionListItem(BaseModel):
    id: str
    movie_title: str
    status: str
    is_favorite: bool
    is_published: bool
    created_at: str
    updated_at: str
