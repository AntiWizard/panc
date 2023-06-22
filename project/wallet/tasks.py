from celery import shared_task
from django.db import transaction

from wallet.functions import reject_cashout_reqeust


@shared_task
@transaction.atomic()
def reject_cashout_reqeust_job():
    reject_cashout_reqeust()
    return True
