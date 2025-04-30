import json
import asyncio
import redis.asyncio as aioredis
from fastapi import WebSocket
from typing import Dict, List
from api.schemas import MessageType, Channels, MessageData, User


class RedisPubSubManager:
	def __init__(self, host='localhost', port=6379, max_saved_messages=25):
		self.redis_host = host
		self.redis_port = port
		self.pubsub = None
		self.redis_connection: aioredis.Redis = None
		self.max_saved_messages = max_saved_messages
		self.subscribed_channels = set()

	async def _get_redis_connection(self) -> aioredis.Redis:
		return aioredis.Redis(
			host=self.redis_host,
			port=self.redis_port,
			decode_responses=True,
			auto_close_connection_pool=False
		)

	async def connect(self) -> None:
		self.redis_connection = await self._get_redis_connection()
		self.pubsub = self.redis_connection.pubsub()

		if not await self.redis_connection.exists(f"chat:messages:{Channels.GLOBAL.value}"):
			await self.redis_connection.set(f"chat:messages:{Channels.GLOBAL.value}", json.dumps([]))

	async def publish(self, channel: str, message: str) -> None:
		await self.redis_connection.publish(channel, message)

	async def subscribe(self, channel: str) -> aioredis.Redis:
		if channel not in self.subscribed_channels:
			await self.pubsub.subscribe(channel)
			self.subscribed_channels.add(channel)
		return self.pubsub

	async def unsubscribe(self, channel: str) -> None:
		if channel in self.subscribed_channels:
			await self.pubsub.unsubscribe(channel)
			self.subscribed_channels.remove(channel)

	async def save_message(self, channel: str, message_data: dict) -> None:
		messages_key = f"chat:messages:{channel}"
		messages_json = await self.redis_connection.get(messages_key)
		messages = json.loads(messages_json) if messages_json else []
		messages.append(message_data)

		if len(messages) > self.max_saved_messages:
			messages = messages[-self.max_saved_messages:]

		await self.redis_connection.set(messages_key, json.dumps(messages))

	async def get_message_history(self, channel: str) -> List[dict]:
		messages_key = f"chat:messages:{channel}"
		messages_json = await self.redis_connection.get(messages_key)
		return json.loads(messages_json) if messages_json else []

	async def initialize_faction_channel(self, faction_id: int) -> None:
		faction_channel = f"{Channels.FACTION.value}:{faction_id}"
		if not await self.redis_connection.exists(f"chat:messages:{faction_channel}"):
			await self.redis_connection.set(f"chat:messages:{faction_channel}", json.dumps([]))
