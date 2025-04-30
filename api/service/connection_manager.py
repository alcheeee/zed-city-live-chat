import json
import asyncio
from fastapi import WebSocket
from typing import Dict, List, Set
from datetime import datetime
from api.schemas import MessageType, Channels, MessageData, User


class WebSocketManager:
	def __init__(self, redis_url='redis://redis:6379', max_saved_messages=25):
		self.rooms: Dict[str, List[WebSocket]] = {}
		self.user_connections: Dict[WebSocket, User] = {}

		from .redis_manager import RedisPubSubManager
		self.pubsub_client = RedisPubSubManager(
			redis_url=redis_url,
			max_saved_messages=max_saved_messages
		)
		self.listeners: Set[asyncio.Task] = set()

	async def connect_user(self, websocket: WebSocket, user: User) -> None:
		self.user_connections[websocket] = user

		if self.pubsub_client.redis_connection is None:
			await self.pubsub_client.connect()

			if not hasattr(self, 'listener_task') or self.listener_task.done():
				self.listener_task = asyncio.create_task(self._listen_to_channel())
				self.listeners.add(self.listener_task)
				self.listener_task.add_done_callback(self.listeners.discard)

		global_channel = Channels.GLOBAL.value
		await self._add_to_room(global_channel, websocket)

		if user.in_faction:
			faction_channel = f"{Channels.FACTION.value}:{user.in_faction}"
			await self.pubsub_client.initialize_faction_channel(user.in_faction)
			await self._add_to_room(faction_channel, websocket)

	async def _add_to_room(self, channel: str, websocket: WebSocket) -> None:
		if channel in self.rooms:
			self.rooms[channel].append(websocket)
		else:
			self.rooms[channel] = [websocket]
			await self.pubsub_client.subscribe(channel)

	async def disconnect_user(self, websocket: WebSocket) -> None:
		if websocket not in self.user_connections:
			return

		user = self.user_connections[websocket]
		await self._remove_from_room(Channels.GLOBAL.value, websocket)

		if user.in_faction:
			faction_channel = f"{Channels.FACTION.value}:{user.in_faction}"
			await self._remove_from_room(faction_channel, websocket)

		del self.user_connections[websocket]

	async def _remove_from_room(self, channel: str, websocket: WebSocket) -> None:
		if channel not in self.rooms:
			return

		if websocket in self.rooms[channel]:
			self.rooms[channel].remove(websocket)

		if len(self.rooms[channel]) == 0:
			del self.rooms[channel]
			await self.pubsub_client.unsubscribe(channel)

	async def broadcast_message(self, channel: Channels, sender: str, message: str) -> None:
		timestamp = datetime.now().isoformat(timespec='seconds')
		message_data = {
			"type": MessageType.MESSAGE,
			"sender": sender,
			"message": message,
			"timestamp": timestamp,
			"channel": channel.split(':')[0]
		}

		if channel.startswith(f"{Channels.FACTION.value}:"):
			faction_id = int(channel.split(':')[1])
			message_data["in_faction"] = faction_id

		await self.pubsub_client.save_message(channel, message_data)
		await self.pubsub_client.publish(channel, json.dumps(message_data))

	async def send_history(self, websocket: WebSocket) -> None:
		if websocket not in self.user_connections:
			return

		user = self.user_connections[websocket]

		global_messages = await self.pubsub_client.get_message_history(Channels.GLOBAL.value)
		if global_messages:
			history_data = {
				"type": MessageType.HISTORY,
				"channel": Channels.GLOBAL.value,
				"messages": global_messages
			}
			await websocket.send_json(history_data)

		if user.in_faction:
			faction_channel = f"{Channels.FACTION.value}:{user.in_faction}"
			faction_messages = await self.pubsub_client.get_message_history(faction_channel)
			if faction_messages:
				history_data = {
					"type": MessageType.HISTORY,
					"channel": Channels.FACTION.value,
					"messages": faction_messages
				}
				await websocket.send_json(history_data)

	async def _listen_to_channel(self) -> None:
		try:
			while True:
				try:
					message = await self.pubsub_client.pubsub.get_message(ignore_subscribe_messages=True)
					if message is not None:
						channel = message['channel']
						data = json.loads(message['data'])

						if channel in self.rooms:
							disconnected = []
							for websocket in self.rooms[channel]:
								try:
									await websocket.send_json(data)
								except Exception as e:
									print(f"Error sending to WebSocket: {str(e)}")
									disconnected.append(websocket)

							for websocket in disconnected:
								await self._remove_from_room(channel, websocket)
								if websocket in self.user_connections:
									del self.user_connections[websocket]

					await asyncio.sleep(0.01)

				except Exception as e:
					print(f"Error in channel listener: {str(e)}")
					await asyncio.sleep(1)

		except asyncio.CancelledError:
			print("PubSub listener task cancelled")
