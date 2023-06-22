from django.db.models import F
from django.utils import timezone
from wallet.models import CashOutRequest, TransactionType, TransactionLog


def reserve_cashout_request(cashout_id):
    pass


def process_cashout_request(cashout_id):
    pass


def reject_cashout_reqeust():  # job -> 1h
    pass