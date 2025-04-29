from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
	username: str
	in_faction: Optional[int] = None

