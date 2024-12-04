import json

from redis.asyncio import Redis


class Tracker:
	def __init__(self, redis_url: str):
		self.redis = Redis.from_url(redis_url)

	async def set_status(self, uuid: str, status: str, result: dict | None) -> None:
		"""
		Set status:

		PENDING
		PROCESSING
		COMPLETED
		FAILED
		"""
		value = json.dumps({"status": status, "task_resuslt": result})
		await self.redis.hset(uuid, uuid, value)

	async def get_status(self, uuid: str) -> None | str:
		status = await self.redis.hget(uuid, uuid)
		return status.decode("utf-8") if status else None
