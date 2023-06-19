from django.urls import path

from lottery.views import BuyTicketView, TicketListView, RoundInfoView

urlpatterns = [
    path('buy/ticket/', BuyTicketView.as_view(), name='buy_ticket'),
    path('ticket/', TicketListView.as_view(), name='ticket_list'),
    path('round/', RoundInfoView.as_view(), name='round_info'),
]
