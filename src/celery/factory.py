from typing import Any, cast

from celery_singleton import Singleton
from src.services.rabbit_mq import RabbitMQ

from celery.app.base import Celery

TASK_LIST = ["src.celery.tasks"]


class TaskContext(Singleton):
    abstract = True

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return cast(Any, Singleton.__call__(self, *args, **kwargs))


def create_celery_app():
    celery = Celery(broker=RabbitMQ.url(), include=TASK_LIST)
    _: Any = celery.config_from_object("src.celery.config")
    celery.Task = TaskContext
    return celery
