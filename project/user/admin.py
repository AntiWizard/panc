from django.contrib import admin

from wallet.models import Wallet, CashOutRequest, Transaction, TransactionLog


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'identifier', 'wallet_type', 'balance', 'flagged_wallet']
    search_fields = ['identifier', 'wallet_type']
    list_filter = ['wallet_type', 'flagged_wallet']


@admin.register(CashOutRequest)
class CashOutRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'type', 'amount', 'is_canceled', 'is_reserved', 'is_processed', 'created_at']
    search_fields = ['user']
    list_filter = ['is_canceled', 'is_reserved', 'is_processed']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet', 'amount', 'currency_type', 'currency_swap', 'status', 'is_swap', 'created_at']
    search_fields = ['wallet']
    list_filter = ['status', 'currency_type', 'currency_swap']


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet', 'amount', 'balance_after', 'temp_transaction_ref', 'transaction_type', 'created_at']
    search_fields = ['wallet', 'temp_transaction_ref']
    list_filter = ['transaction_type']
