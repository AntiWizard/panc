from django.urls import path

from wallet.views import (
    CashoutListView,
    CashoutDetailView,
    TransactionLogListView,
    ConvertToUSDView,
    SwapDefaultView,
    FirstStepSwapView,
    SecondStepSwapView
)

urlpatterns = [
    path('swap/default/', SwapDefaultView.as_view(), name='swap_default'),
    path('convert-to-usd/', ConvertToUSDView.as_view(), name='convert_to_usd'),
    path('cashout-list/', CashoutListView.as_view(), name='cashout_list'),
    path('cashout/<int:pk>/', CashoutDetailView.as_view(), name='cashout_detail'),
    path('transaction-list/', TransactionLogListView.as_view(), name='transaction_list'),
    path('show_swap_currencies/', FirstStepSwapView.as_view(), name='show_swap_currencies'),
    path('Create_transaction/', SecondStepSwapView.as_view(), name='Create_transaction'),
]
