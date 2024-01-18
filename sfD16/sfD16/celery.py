import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sfD16.settings')

app = Celery('sfD16')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'action_every_monday_8am': {
        'task': 'posts.tasks.maildelivery',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'), # каждый пнд 8 утра monday
        'args': (),
    },
}