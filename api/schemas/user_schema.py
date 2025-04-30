from typing import Optional
from pydantic import BaseModel


class User(BaseModel):
	username: str
	user_id: Optional[int] = 0
	in_faction: Optional[int] = None

