from django.urls import path

from lottery.views import BuyTicketView, TicketListView, PreviousRoundInfoView, CurrentRoundInfoView

urlpatterns = [
    path('buy/ticket/', BuyTicketView.as_view(), name='buy_ticket'),
    path('ticket/', TicketListView.as_view(), name='ticket_list'),
    path('previous-round/', PreviousRoundInfoView.as_view(), name='pre_round_info'),
    path('current-round/', CurrentRoundInfoView.as_view(), name='current_round_info'),
]
