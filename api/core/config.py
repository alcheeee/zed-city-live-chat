from os import getenv


class Config:
	FASTAPI_THREAD_TOKENS = int(getenv("FASTAPI_THREAD_TOKENS", "40"))
	MAX_SAVED_MESSAGES = int(getenv("MAX_SAVED_MESSAGES", "25"))
	REDIS_HOST = getenv("REDIS_HOST", "localhost")
	REDIS_PORT = int(getenv("REDIS_PORT", "6379"))


config = Config()
