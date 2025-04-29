from fastapi import APIRouter, Depends
from api.core.config import config
from api.routers.chat_router import router as chat_router


router = APIRouter()

@router.get("/status")
async def status() -> str | dict:
	return {'status': 'ok'}


router.include_router(
	chat_router, prefix="/chat"
)
