import decimal

from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from config.models import GlobalConfig
from lottery.functions import generate_ticket_number
from lottery.models import RoundInfo, Ticket, RoundDetail
from user.models import User
from user.permissions import IsAuthenticatedPanc
from wallet.constants import WalletType, TransactionType
from wallet.models import Wallet, TransactionLog


class BuyTicketView(GenericAPIView):
    permission_classes = [IsAuthenticatedPanc]

    def post(self, request):
        user_id = request.user_id
        user = User.objects.filter(id=user_id, is_active=True).first()

        if not user:
            return Response(data={'message': 'Bad Request'}, status=400)

        round_info_qs = RoundInfo.objects.filter(is_done=False)
        if len(round_info_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        burn_ratio_obj = GlobalConfig.objects.filter(config_name='BURN_RATIO').first()
        if not burn_ratio_obj:
            return Response(data={'message': 'Internal server error'}, status=500)

        wallet_qs = Wallet.objects.filter(wallet_type=WalletType.USD, identifier=user.wallet_address)

        if len(wallet_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        ticket_number = generate_ticket_number()

        with transaction.atomic():
            main_wallet_obj = Wallet.objects.filter(wallet_type=WalletType.MAIN,
                                                    flagged_wallet=True).select_for_update().get()

            round_info = round_info_qs.select_for_update().first()

            wallet_user = wallet_qs.select_for_update().first()
            if wallet_user.balance < round_info.ticket_amount:
                return Response(data={'message': 'Bad Request'}, status=400)

            round_info.ticket_count += 1
            round_info.total_price += round_info.ticket_amount
            round_info.burn_amount += (
                    round_info.ticket_amount * decimal.Decimal(str(float(burn_ratio_obj.config_value) / 100)))
            round_info.save()

            wallet_user.balance -= round_info.ticket_amount
            wallet_user.save()

            main_wallet_obj.balance += round_info.ticket_amount
            main_wallet_obj.save()

            Ticket.objects.create(round=round_info, user=user, number=ticket_number)

            TransactionLog.objects.create(wallet=wallet_user, amount=-round_info.ticket_amount,
                                          transaction_type=TransactionType.LOTTERY)

            TransactionLog.objects.create(wallet=main_wallet_obj, amount=+round_info.ticket_amount,
                                          transaction_type=TransactionType.LOTTERY)

        data = {'ticket_number': ticket_number, 'ticket_amount': round_info.ticket_amount}

        return Response(data={'message': 'OK', 'data': data}, status=200)


class TicketListView(GenericAPIView):
    permission_classes = [IsAuthenticatedPanc]

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


class PreviousRoundInfoView(GenericAPIView):

    def get(self, request):
        round_info_qs = RoundInfo.objects.filter(is_done=False)
        if len(round_info_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        previous_round_info = round_info_qs.first().previous_round
        if not previous_round_info.is_done:
            return Response(data={'message': 'Internal server error'}, status=500)

        previous_round_details_qs = RoundDetail.objects.filter(round=previous_round_info)
        if not previous_round_info:
            data = {
                'round_number': None,
                'total_price': 0,
                'ticket_count': 0,
                'ticket_goal': None,
                'ticket_amount': 0,
                'burn_amount': 0
            }
        else:
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


class CurrentRoundInfoView(GenericAPIView):

    def get(self, request):
        fake_price_obj = GlobalConfig.objects.filter(config_name='FAKE_ROUND_PRICE').first()
        if not fake_price_obj:
            return Response(data={'message': 'Internal server error'}, status=500)

        round_info_qs = RoundInfo.objects.filter(is_done=False)
        if len(round_info_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)
        round_info = round_info_qs.first()

        data = {
            'round_number': round_info.number,
            'total_price': (round_info.total_price + decimal.Decimal(str(fake_price_obj.config_value)))
        }

        return Response(data={'message': 'OK', 'data': data}, status=200)
