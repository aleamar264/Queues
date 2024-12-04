import asyncio
from typing import AsyncIterable

from faust import StreamT
from faust_tools.config import app, input_testing_1, input_testing_2
from redis_records.track import Tracker
from schemas.schema import Input, Output

tracker = Tracker(redis_url="redis://redis.default.svc.cluster.local:6379/1")


@app.agent(input_testing_1, concurrency=5)
async def process_task1(stream: StreamT[Input]) -> AsyncIterable[Output]:
	async for task in stream:
		if (uuid := task.uuid) is not None:
			await tracker.set_status(uuid=uuid, status="PROCESSING", result={})
		try:
			await asyncio.sleep(15)
			task_return = Output(name_task=task.name, state="complete")
			await tracker.set_status(
				uuid=uuid, status="COMPLETED", result=task_return.model_dump()
			)
			print(task_return.model_dump())
			yield task_return
		except Exception as err:
			if uuid is not None:
				await tracker.set_status(uuid=uuid, status="FAILED", result=None)
			print(f"Error processing message {uuid}: {err}")


@app.agent(input_testing_2, concurrency=5)
async def process_task2(stream: StreamT[Input]) -> AsyncIterable[Output]:
	async for task in stream:
		if (uuid := task.uuid) is not None:
			print(uuid)
			await tracker.set_status(uuid=uuid, status="PROCESSING", result={})
		try:
			await asyncio.sleep(10)
			task_return = Output(name_task=task.name, state="complete")
			await tracker.set_status(
				uuid=uuid, status="COMPLETED", result=task_return.model_dump()
			)
			print(task_return.model_dump())
			yield task_return
		except Exception as err:
			if uuid is not None:
				await tracker.set_status(uuid=uuid, status="FAILED", result=None)
			print(f"Error processing message {uuid}: {err}")
