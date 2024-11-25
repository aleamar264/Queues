import os
from functools import lru_cache
from typing import Any

from kombu import Queue  # type: ignore


def route_task(
    name: str,
    args: Any,
    kwargs: Any,
    options: Any,
    task: Any = None,
    **kw: dict[str, Any],
) -> dict[str, str]:
    if ":" in name:
        queue, _ = name.split(":")
        return {"queue": queue}
    return {"queue": "celery"}


class BaseConfig:
    CELERY_BROKER_URL: str = os.environ.get(
        "CELERY_BROKER_URL",
        "amqp://rabbitmq:rabbitmq@rabbitmq-headless.default.svc.cluster.local:5672//",
    )
    CELERY_RESULT_BACKEND: str = os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://redis.default.svc.cluster.local:6379/0"
    )

    CELERY_TASK_QUEUES: tuple[Queue, Queue] = (
        # default queue
        Queue("celery"),
        # custom queue
        Queue("Test_Query"),
    )

    CELERY_TASK_ROUTES = (route_task,)


class DevelopmentConfig(BaseConfig):
    pass


@lru_cache()
def get_settings() -> DevelopmentConfig:
    config_cls_dict = {
        "development": DevelopmentConfig,
    }
    config_name = os.environ.get("CELERY_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
