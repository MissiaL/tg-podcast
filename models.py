from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel
from pydantic import HttpUrl


class Post(BaseModel):
    name: str
    url: HttpUrl
    title: str
    text: str
    created_at: datetime = datetime.now(timezone.utc)
    published_at: Optional[str]
    file_path: str
    file_deleted: bool = False
