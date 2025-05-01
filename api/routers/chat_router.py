import json
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api.schemas import MessageType, Channels, MessageData, User

router = APIRouter(prefix='/chat')


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	socket_manager = websocket.app.state.socket_manager
	await websocket.accept()

	try:
		user_data = await websocket.receive_json()
		user = User(**user_data)

		await socket_manager.connect_user(websocket, user)
		await socket_manager.send_history(websocket)

		welcome_message = {
			"type": MessageType.MESSAGE,
			"sender": "System",
			"message": f"Welcome, {user.username}! There are {len(socket_manager.user_connections)} users in chat!",
			"channel": Channels.GLOBAL.value,
			"timestamp": datetime.now().isoformat(timespec='seconds')
		}
		await websocket.send_json(welcome_message)
		faction_prefix_len = len("/faction ")

		while True:
			data = await websocket.receive_text()
			if data.startswith("/faction "):
				faction_message = data[faction_prefix_len:]

				if user.in_faction:
					faction_channel = f"{Channels.FACTION.value}:{user.in_faction}"
					await socket_manager.broadcast_message(
						channel=faction_channel,
						sender=user.username,
						message=faction_message
					)
				else:
					error_message = {
						"type": MessageType.MESSAGE,
						"sender": "System",
						"message": "You're not in a faction.",
						"channel": Channels.GLOBAL.value,
						"timestamp": datetime.now().isoformat(timespec='seconds')
					}
					await websocket.send_json(error_message)
			else:
				await socket_manager.broadcast_message(
					channel=Channels.GLOBAL.value,
					sender=user.username,
					message=data
				)

	except WebSocketDisconnect:
		await socket_manager.disconnect_user(websocket)

	except Exception as e:
		print(f"WebSocket error: {str(e)}")
		try:
			await socket_manager.disconnect_user(websocket)
		except:
			pass