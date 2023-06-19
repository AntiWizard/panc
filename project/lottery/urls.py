from django.urls import path

from lottery.views import BuyTicketView, TicketListView, RoundInfoView

urlpatterns = [
    path('lottery/buy/ticket/', BuyTicketView.as_view(), name='buy_ticket'),
    path('lottery/ticket/', TicketListView.as_view(), name='ticket_list'),
    path('lottery/round/', RoundInfoView.as_view(), name='round_info'),
]
