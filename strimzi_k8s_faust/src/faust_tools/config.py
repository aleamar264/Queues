import os

from faust import App

from .faust_schema.schema import Input

STORE_DATA = "redis://redis.default.svc.cluster.local:6379/0"

BROKER_KAFKA: str = os.environ.get(
	"KAFKA_RESULT_BACKEND",
	"aiokafka://my-cluster-kafka-bootstrap.kafka.svc.cluster.local",
	# "aiokafka://my-cluster-kafka-brokers.kafka.svc.cluster.local:9092",
)

app = App(
	"example",
	broker=BROKER_KAFKA,
	# store=STORE_DATA,
	autodiscover=True,
	origin="faust_tools",
)

input_testing_1 = app.topic("task_1", value_type=Input, partitions=3)
input_testing_2 = app.topic("task_2", value_type=Input, partitions=3)
