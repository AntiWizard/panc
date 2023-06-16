from django.db import models
from django.db.models import UniqueConstraint

from user.models import AbstractBaseModelWithUUidAsPk, User
from wallet.constants import WalletType, TransactionStatus, CurrencyType, TransactionType


class Wallet(AbstractBaseModelWithUUidAsPk):  # wallet site
    identifier = models.CharField(max_length=42)  # wallet_address user / owner
    wallet_type = models.CharField(choices=WalletType.CHOICES, default=WalletType.USD)
    balance = models.FloatField(default=0.0)
    flagged_wallet = models.BooleanField(default=False, blank=False, null=False)

    def __str__(self):
        return self.identifier

    class Meta:
        UniqueConstraint('identifier', 'wallet_type', name="unique_identifier_wallet_type")


class CashOutRequest(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.DO_NOTHING)
    type = models.CharField(choices=WalletType.CHOICES, default=WalletType.USD)
    amount = models.FloatField()
    is_canceled = models.BooleanField(default=False)
    is_reserved = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)
    description = models.CharField(default=None, null=True, blank=True, max_length=500)

    canceled_at = models.DateTimeField(default=None, null=True, blank=True)
    reserved_at = models.DateTimeField(default=None, null=True, blank=True)
    processed_at = models.DateTimeField(default=None, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    def get_status_dict(self):
        if self.is_canceled:
            return_dict = {'status': 'Canceled', 'status_code': 1}
        else:
            if self.is_processed:
                return_dict = {'status': 'Sent to bank', 'status_code': 3}
            else:
                if self.is_reserved:
                    return_dict = {'status': 'Processing', 'status_code': 2}
                else:
                    return_dict = {'status': 'Awaiting process', 'status_code': 0}
        return return_dict


class Transaction(AbstractBaseModelWithUUidAsPk):
    amount = models.FloatField()
    wallet = models.ForeignKey(to=Wallet, on_delete=models.CASCADE)
    currency_type = models.CharField(choices=CurrencyType.CHOICES, default=CurrencyType.USD)
    currency_swap = models.CharField(choices=CurrencyType.CHOICES, default=CurrencyType.USD, null=True, blank=True)

    status = models.CharField(choices=TransactionStatus.CHOICES, default=TransactionStatus.CHOICES)
    is_swap = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)


class TransactionLog(AbstractBaseModelWithUUidAsPk):
    wallet = models.ForeignKey(to=Wallet, on_delete=models.DO_NOTHING)
    amount = models.FloatField()
    balance_after = models.FloatField(default=0)
    temp_transaction_ref = models.CharField(max_length=36, null=True, blank=True, default=None)
    transaction_type = models.CharField(choices=TransactionType.CHOICES, default=TransactionType.TRANSACTION)

    created_at = models.DateTimeField(auto_now_add=True, editable=False)
