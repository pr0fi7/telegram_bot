from celery import Celery
import os

celery = Celery('telegrambot',
                broker=os.getenv('CELERY_BROKER_URL',),
                backend=os.getenv('CELERY_RESULT_BACKEND'))
import handle_file
celery.autodiscover_tasks(['handle_file'])
