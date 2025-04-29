from typing import List, Dict
from datetime import datetime
from fastapi.responses import HTMLResponse
from fastapi import WebSocket
from api.schemas import User


class ConnectionManager:
	def __init__(self):
		self.active_connections: list[WebSocket] = []
		self.user_data: Dict[WebSocket, User] = {}
		self.global_messages: List[Dict[str, str]] = []  # {'sender':'', 'message':'', 'timestamp':0}
		self.max_saved_messages = 25

	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.active_connections.append(websocket)

	async def disconnect(self, websocket: WebSocket):
		if websocket in self.active_connections:
			self.active_connections.remove(websocket)
		if websocket in self.user_data:
			del self.user_data[websocket]

	async def register_user(self, websocket: WebSocket, user: User):
		self.user_data[websocket] = user

	async def send_history(self, websocket: WebSocket):
		if self.global_messages:
			await websocket.send_json({
				"type": "history",
				"messages": self.global_messages
			})

	async def broadcast(self, data: str, sender: str):
		timestamp = datetime.now().isoformat(timespec='seconds')
		message_data = {"sender": sender, "message": data, "timestamp": timestamp}

		self.global_messages.append(message_data)
		if len(self.global_messages) > self.max_saved_messages:
			self.global_messages.pop(0)

		data_to_send = {
			"type": "message",
			"sender": sender,
			"message": data,
			"channel": "global",
			"timestamp": timestamp
		}
		for connection in self.active_connections:
			await connection.send_json(data_to_send)

	async def broadcast_to_faction(self, in_faction: str, data: str, sender: str):
		timestamp = datetime.now().isoformat(timespec='seconds')
		data_to_send = {
			"type": "message",
			"sender": sender,
			"message": data,
			"channel": "faction",
			"timestamp": timestamp
		}
		for websocket, user in self.user_data.items():
			if user.in_faction == in_faction:
				await websocket.send_json(data_to_send)
