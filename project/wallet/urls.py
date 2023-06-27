from django.urls import path

from wallet.views import (
    FirstStepSwapView,
    SecondStepSwapView,
    CashoutListView,
    CashoutDetailView,
    TransactionLogListView,
    ConvertToUSDView,
    SwapDefaultView,
)

urlpatterns = [
    path('first-step/swap/', FirstStepSwapView.as_view(), name='swap_first_step'),
    path('second-step/swap/', SecondStepSwapView.as_view(), name='swap_second_step'),
    path('swap/default/', SwapDefaultView.as_view(), name='swap_default'),
    path('convert-to-usd/', ConvertToUSDView.as_view(), name='convert_to_usd'),
    path('cashout-list/', CashoutListView.as_view(), name='cashout_list'),
    path('cashout/<int:pk>/', CashoutDetailView.as_view(), name='cashout_detail'),
    path('transaction-list/', TransactionLogListView.as_view(), name='transaction_list'),
]
