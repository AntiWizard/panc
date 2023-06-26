from django.urls import path

from wallet.views import (
    SwapView,
    CashoutListView,
    CashoutDetailView,
    TransactionLogListView,
    ConvertToUSDView,
    SwapDefaultView,
    TransactionView,
)

urlpatterns = [
    path('swap/', SwapView.as_view(), name='swap'),
    path('swap/default/', SwapDefaultView.as_view(), name='swap_default'),
    path('convert-to-usd/', ConvertToUSDView.as_view(), name='convert_to_usd'),
    path('cashout-list/', CashoutListView.as_view(), name='cashout_list'),
    path('cashout/<int:pk>/', CashoutDetailView.as_view(), name='cashout_detail'),
    path('transaction-list/', TransactionLogListView.as_view(), name='transaction_list'),
    path('transaction/', TransactionView.as_view(), name='transaction_create'),
]
