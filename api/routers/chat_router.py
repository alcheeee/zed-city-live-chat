import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from api.service import manager
from api.schemas import User


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	await manager.connect(websocket)

	try:
		user_data = await websocket.receive_json()
		user = User(**user_data)
		await manager.register_user(websocket, user)

		while True:
			data = await websocket.receive_text()

			if data.startswith("/faction "):
				faction_message = data[len("/faction "):]

				if user.in_faction:
					await manager.broadcast_to_faction(user.in_faction, faction_message, user.username)
				else:
					await websocket.send_json({
						"type": "message",
						"sender": "System",
						"message": "You're not in a faction.",
						"channel": "faction",
						"timestamp": datetime.now().isoformat(timespec='seconds')
					})
			else:
				await manager.broadcast(data, user.username)

	except WebSocketDisconnect:
		await manager.disconnect(websocket)

