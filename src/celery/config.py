
from typing import TypedDict

from celery.schedules import crontab
from src.services.environment import Environment


class BeatTask(TypedDict):
    task: str
    schedule: crontab


CELERY_BROKER_URL = Environment.RABBIT_MQ_URL
CELERY_RESULT_BACKEND = Environment.REDIS_MOD_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERYBEAT_SCHEDULE: dict[str, BeatTask] = {
    "reddit": {"task": "scrapper", "schedule": crontab(minute='*/5')},
    "ai": {"task": "model_runner", "schedule": crontab(minute='*/5')}
}
