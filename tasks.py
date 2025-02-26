from celery import Celery

# Create a new Celery instance
app = Celery('tasks', broker='redis://localhost:6379/0')

# Load task modules (if any)
app.autodiscover_tasks()
