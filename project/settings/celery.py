import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
app = Celery('panc')

app.conf.timezone = 'UTC'

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'lottery_process_job': {
        'task': 'lottery.tasks.lottery_process_job',
        'schedule': crontab(hour='*/4'),
    },
    'check_if_not_winner_processed_job': {
        'task': 'lottery.tasks.check_if_not_winner_processed_job',
        'schedule': crontab(minute='30', hour='*/2'),
    },
    'reject_cashout_reqeust_job': {
        'task': 'wallet.tasks.reject_cashout_reqeust_job',
        'schedule': crontab(minute='30', hour='*/2'),
    },
}
