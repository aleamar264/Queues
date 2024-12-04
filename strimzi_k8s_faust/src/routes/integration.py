import json
from typing import Annotated, AsyncGenerator
from uuid import UUID, uuid4

from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, Path, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from redis.asyncio import Redis
from schemas.schema import Input

route = APIRouter(prefix="/test", tags=["strimzi"])


class taskId(BaseModel):
	task_id: str


async def get_redis() -> AsyncGenerator[Redis, None]:
	redis = Redis.from_url("redis://redis.default.svc.cluster.local:6379/1")
	try:
		yield redis
	finally:
		await redis.close()


@route.post("/")
async def queue(
	request: Request, input_: Input, redis: Redis = Depends(get_redis)
) -> JSONResponse:
	producer: AIOKafkaProducer = request.app.state.producer
	uuid = str(uuid4())
	value = json.dumps({"status": "PENDING", "task_resuslt": {}})
	input_.uuid = uuid
	if input_.task == "task_1":
		await redis.hset(name=uuid, key=uuid, value=value)  # type: ignore
		await producer.send_and_wait("task_1", input_.model_dump_json().encode())
		return JSONResponse({"message": "Task 1 in queue", "uuid": uuid})
	elif input_.task == "task_2":
		await redis.hset(name=uuid, key=uuid, value=value)  # type: ignore
		await producer.send_and_wait("task_2", input_.model_dump_json().encode())
		return JSONResponse({"message": "Task 2 in queue", "uuid": uuid})
	return JSONResponse(
		{"message": "Only task_1 or task_2 is valid here, try again"}, status_code=400
	)


@route.get("/task/{task_id}")
async def queue_result(
	task_id: Annotated[str, Path()], redis: Redis = Depends(get_redis)
) -> JSONResponse:
	try:
		uuid_ = UUID(task_id, version=4)
	except (ValueError, TypeError):
		return JSONResponse({"message": f"The UUID {task_id} is not valid"})
	uuid = str(uuid_)
	track = await redis.hget(uuid, uuid)  # type: ignore
	track_dict = json.loads(track)
	return JSONResponse(
		{
			"message": f"Task with id {task_id} is {(status:=track_dict.get("status"))}",
			"status": status,
			"task_result": track_dict["task_resuslt"],
		}
	)
