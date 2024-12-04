from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from routes.integration import route


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[AIOKafkaProducer]:
	producer = AIOKafkaProducer(
		bootstrap_servers="my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092",
	)
	await producer.start()
	try:
		app.state.producer = producer
		yield
	finally:
		producer.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(route)
