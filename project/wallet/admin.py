from django.contrib import admin

from wallet.models import Wallet, CashOutRequest, Transaction, TransactionLog


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['id', 'identifier', 'wallet_type', 'balance', 'flagged_wallet']
    search_fields = ['identifier', 'wallet_type']
    list_filter = ['wallet_type', 'flagged_wallet']
    ordering = ['-flagged_wallet', '-balance']


@admin.register(CashOutRequest)
class CashOutRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet', 'type', 'amount', 'is_canceled', 'is_reserved', 'is_processed', 'created_at']
    search_fields = ['wallet']
    list_filter = ['is_canceled', 'is_reserved', 'is_processed']
    ordering = ['-created_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'wallet', 'amount', 'currency_type', 'currency_swap', 'status', 'is_swap', 'created_at']
    search_fields = ['wallet']
    list_filter = ['status', 'currency_type', 'currency_swap']
    ordering = ['-created_at']


@admin.register(TransactionLog)
class TransactionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_type', 'amount', 'wallet', 'temp_transaction_ref', 'created_at']
    search_fields = ['wallet', 'temp_transaction_ref']
    list_filter = ['transaction_type']
    ordering = ['-created_at']
