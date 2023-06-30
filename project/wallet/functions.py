from django.db import transaction
from django.utils import timezone

from utils.ex_request import convert_currency_to_usd
from wallet.models import CashOutRequest


def process_cashout_request():
    pass


def reserve_cashout_reqeust():
    pass


def reject_cashout_reqeust():
    cashout_qs = CashOutRequest.objects.filter(is_processed=False, is_reserved=False, is_canceled=False) \
        .order_by('-created_at').select_related('wallet')

    with transaction.atomic():
        for request in cashout_qs:
            wallet_balance = request.wallet.balance
            balance_from_usd = convert_currency_to_usd(request.type).get('USD')
            if not balance_from_usd:
                continue
            balance_usd = balance_from_usd * request.amount
            if balance_usd > wallet_balance:
                request.is_canceled = True
                request.canceled_at = timezone.now()
                request.description = f'Wallet balance : {wallet_balance} not enough'
                request.save()
