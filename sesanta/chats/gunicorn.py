# Gunicorn configuration

from sesanta.settings import settings

bind = f"{settings.chats_host}:{settings.chats_port}"
workers = settings.chats_workers
worker_class = "uvicorn.workers.UvicornWorker"
