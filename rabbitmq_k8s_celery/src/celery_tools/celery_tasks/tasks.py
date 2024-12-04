from time import sleep

from celery import shared_task  # type: ignore
from schemas.schemas import Input, Ouput


@shared_task(
	bind=True,
	autoretry_for=(Exception,),
	retry_backoff=True,
	retry_kwargs={"max_retries": 5},
	name="Test_Query:task_1",
	acks_late=True,
)  # type: ignore
def task_1(self, input_: Input) -> Ouput:
	sleep(15)
	return Ouput(name_task=input_.name, state="complete")


@shared_task(
	bind=True,
	autoretry_for=(Exception,),
	retry_backoff=True,
	retry_kwargs={"max_retries": 5},
	name="Test_Query:task_2",
	acks_late=True,
)  # type: ignore
def task_2(self, input_: Input) -> Ouput:
	sleep(10)
	return Ouput(name_task=input_.name, state="complete")
