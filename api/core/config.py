from os import getenv


class Config:
	FASTAPI_THREAD_TOKENS = int(getenv("FASTAPI_THREAD_TOKENS", "40"))
	MAX_SAVED_MESSAGES = int(getenv("MAX_SAVED_MESSAGES", "25"))
	REDIS_URL = getenv("REDIS_URL", "redis://redis:6379")


config = Config()
