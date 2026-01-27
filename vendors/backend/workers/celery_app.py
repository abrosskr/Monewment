from celery import Celery
import os

# RabbitMQ or Redis URL
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "vendors_worker",
    broker=BROKER_URL,
    backend=BACKEND_URL,
    include=['workers.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Seoul',
    enable_utc=True,
)

if __name__ == '__main__':
    celery_app.start()
