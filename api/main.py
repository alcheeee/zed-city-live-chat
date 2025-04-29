from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

import uvicorn
from anyio import to_thread
from fastapi import FastAPI

from api.core.config import config
from api.routers import router


# brave.exe --user-data-dir="C://Chrome dev session" --disable-web-security


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator:
	to_thread.current_default_thread_limiter().total_tokens = config.FASTAPI_THREAD_TOKENS

	yield


server = FastAPI(
	title="Zed City Live Chat",
	lifespan=lifespan
)

server.include_router(router, prefix="/api")



if __name__ == "__main__":
	uvicorn.run(server, host="0.0.0.0", port=8000)
