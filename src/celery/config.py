import os

from celery.schedules import crontab

CELERY_BROKER_URL = "pyamqp://rabbitmq:5672"
CELERY_RESULT_BACKEND = f"redis://{os.environ['REDIS_MOD_HOST']}:{os.environ['REDIS_MOD_PORT']}"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERYBEAT_SCHEDULE = {
    "reddit": {"task": "scrapper", "schedule": crontab(minute='*/5')},
    "ai": {"task": "model_runner", "schedule": crontab(minute='*/5')},
    "template": {"task": "sync", "schedule": crontab(minute="0", hour="0")}
}
