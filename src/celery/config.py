from celery.schedules import crontab

CELERY_BROKER_URL = "pyamqp://rabbitmq:5672"
CELERY_RESULT_BACKEND = "redis://redismod:6379"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_REDIS_MAX_CONNECTIONS = 5
CELERYBEAT_SCHEDULE = {
    "reddit": {"task": "RedditScrapper3", "schedule": crontab(minute='*/5')},
    "ai_model_runner": {"task": "AiModelRunner", "schedule": crontab(minute='*/5')}
}
