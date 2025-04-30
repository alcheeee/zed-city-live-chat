from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from anyio import to_thread
from fastapi import FastAPI

from api.core.config import config
from api.routers import router
from api.service.connection_manager import WebSocketManager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
	to_thread.current_default_thread_limiter().total_tokens = config.FASTAPI_THREAD_TOKENS

	socket_manager = WebSocketManager(
		redis_host=config.REDIS_HOST,
		redis_port=config.REDIS_PORT,
		max_saved_messages=config.MAX_SAVED_MESSAGES
	)
	app.state.socket_manager = socket_manager

	yield


server = FastAPI(
	title="Zed City Live Chat",
	lifespan=lifespan
)

server.include_router(router, prefix="/api")
