from typing import Any

from celery import current_app as current_celery_app  # type: ignore
from celery.local import Proxy  # type: ignore
from celery.result import AsyncResult  # type: ignore
from kombu.serialization import register  # type: ignore

from celery_tools.serializer import pydanticserializer
from celery_tools.serializer.pydanticserializer import register_pydantic_types
from schemas.schemas import Input, Ouput

from .celery_config import settings


def register_pydantic_model() -> None:
    register(
        "pydantic",
        pydanticserializer.pydantic_dupms,
        pydanticserializer.pydantic_loads,
        content_type="application/x-pydantic",
        content_encoding="utf-8",
    )


def create_celery() -> Proxy:
    # register_pydantic_model()
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace="CELERY")
    celery_app.conf.update(task_track_started=True)
    # celery_app.conf.update(task_serializer="pydantic")
    # celery_app.conf.update(result_serializer="pydantic")
    # celery_app.conf.update(event_serializer="pydantic")
    celery_app.conf.update(task_serializer="json")
    celery_app.conf.update(result_serializer="json")
    celery_app.conf.update(event_serializer="json")
    celery_app.conf.update(
        accept_content=["application/json", "application/x-pydantic"]
    )
    celery_app.conf.update(
        result_accept_content=["application/json", "application/x-pydantic"]
    )
    celery_app.conf.update(worker_concurrency=1)
    celery_app.conf.update(worker_max_tasks_per_child=100)
    celery_app.conf.update(worker_heartbeat=120)
    celery_app.conf.update(result_expires=200)
    celery_app.conf.update(result_persistent=True)
    celery_app.conf.update(enable_utc=True)
    celery_app.conf.update(worker_send_task_events=False)
    celery_app.conf.update(worker_prefetch_multiplier=2)
    celery_app.conf.update(task_acks_late=True)
    celery_app.conf.update(task_reject_on_worker_lost=True)
    celery_app.conf.update(broker_pool_limit=5)

    register_pydantic_types(Input, Ouput)

    return celery_app


def get_task_info(task_id: str) -> dict[str, Any]:
    """
    return task info for the given task_id
    """
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return result
