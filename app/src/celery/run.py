from celery import Celery
from src.celery.config import celery_settings

celery_app = Celery('excel_parser', include=['src.celery.tasks'])
celery_app.config_from_object(celery_settings)
celery_app.autodiscover_tasks(['src.celery'])
