from fastapi import APIRouter, Depends
from api.core.config import config
from api.routers.chat_router import router


@router.get("/status")
async def status() -> str | dict:
	return {'status': 'ok'}
