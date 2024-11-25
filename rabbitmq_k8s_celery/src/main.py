from fastapi import FastAPI

from celery_tools.config.celery_utils import create_celery
from routes.intregration import router

app = FastAPI()
app.celery_app = create_celery()  # type: ignore
app.include_router(router)

celery = app.celery_app  # type: ignore
