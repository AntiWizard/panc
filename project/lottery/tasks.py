from celery import shared_task
from django.db import transaction

from lottery.functions import lottery_process, check_if_not_winner_processed


@shared_task
@transaction.atomic()
def lottery_process_job():
    lottery_process()
    return True


@shared_task
@transaction.atomic()
def check_if_not_winner_processed_job():
    check_if_not_winner_processed()
    return True
