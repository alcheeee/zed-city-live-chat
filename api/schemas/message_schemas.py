from enum import Enum
from datetime import datetime
from pydantic import BaseModel

class MessageType(str, Enum):
	MESSAGE = "message"
	HISTORY = "history"

class Channels(str, Enum):
	GLOBAL = "global"
	FACTION = "faction"

class MessageData(BaseModel):
	type: MessageType
	sender: str
	message: str
	timestamp: datetime
	channel: Channels

