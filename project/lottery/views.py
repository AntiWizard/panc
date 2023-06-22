from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from lottery.functions import generate_ticket_number
from lottery.models import RoundInfo, Ticket, RoundDetail
from user.models import User
from user.permissions import IsAuthenticatedPenc
from wallet.constants import WalletType
from wallet.models import Wallet


class BuyTicketView(GenericAPIView):
    permission_classes = [IsAuthenticatedPenc]

    def post(self, request):
        user_id = request.user_id
        user = User.objects.filter(id=user_id, is_active=True).first()

        if not user:
            return Response(data={'message': 'Bad Request'}, status=400)

        round_info_qs = RoundInfo.objects.filter(is_done=False)
        if len(round_info_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        round_obj = round_info_qs.first()
        wallet_qs = Wallet.objects.filter(wallet_type=WalletType.USD, identifier=user.wallet_address)

        if len(wallet_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        wallet_user = wallet_qs.first()

        if wallet_user.balance < round_obj.ticket_amount:
            return Response(data={'message': 'Bad Request'}, status=400)

        ticket_number = generate_ticket_number()
        Ticket.objects.create(round=round_obj, user=user, number=ticket_number)
        data = {'ticket_number': ticket_number, 'ticket_amount': round_obj.ticket_amount}

        return Response(data={'message': 'OK', 'data': data}, status=200)


class TicketListView(GenericAPIView):
    permission_classes = [IsAuthenticatedPenc]

    def get(self, request):
        user_id = request.user_id
        user = User.objects.filter(id=user_id, is_active=True).first()

        if not user:
            return Response(data={'message': 'Bad Request'}, status=400)

        ticket_qs = Ticket.objects.filter(user=user, is_active=True).select_related('round').order_by('-created_at')
        data = []
        for ticket_obj in ticket_qs:
            data.append({
                'ticket_number': ticket_obj.number,
                'amount': ticket_obj.round.ticket_amount,
                'round_number': ticket_obj.round.number,
                'created_at': ticket_obj.created_at
            })

        return Response(data={'message': 'OK', 'data': data}, status=200)


class RoundInfoView(GenericAPIView):

    def get(self, request):
        round_info_qs = RoundInfo.objects.filter(is_done=False).select_related('previous_round')
        if len(round_info_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        previous_round_info = round_info_qs.first().previous_round
        if not previous_round_info.is_done:
            return Response(data={'message': 'Internal server error'}, status=500)

        previous_round_details_qs = RoundDetail.objects.filter(round=previous_round_info)
        data = {
            'round_number': previous_round_info.number,
            'total_price': previous_round_info.total_price,
            'ticket_count': previous_round_info.ticket_count,
            'ticket_goal': previous_round_info.ticket_goal,
            'ticket_amount': previous_round_info.ticket_amount,
            'burn_amount': previous_round_info.burn_amount
        }

        for detail in previous_round_details_qs:
            data[detail.type] = {
                'count': detail.count,
                'total_amount': detail.total_amount,
            }

        return Response(data={'message': 'OK', 'data': data}, status=200)
