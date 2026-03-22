from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class ApiUser(SQLModel, table=True):
    __tablename__ = "api_users"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    api_key_hash: str = Field(index=True, unique=True)
    active: bool = Field(default=True)
    is_internal: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    curr_credits: int = Field(default=1000)
