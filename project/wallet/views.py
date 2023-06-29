import decimal
from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import requests
from web3 import Web3
from django.conf import settings
from config.models import GlobalConfig
from user.models import User
from user.permissions import IsAuthenticatedPanc
from utils.ex_request import convert_currency_to_usdt
from wallet.constants import WalletType, CurrencyType
from wallet.models import TransactionLog, Wallet, CashOutRequest, Transaction
from wallet.serializers import CashoutRequestSerializer, SwapSerializer, ConvertToUSDSerializer, SecondSwapSerializer


class ConvertToUSDView(GenericAPIView):
    serializer_class = ConvertToUSDSerializer

    def get(self, request):
        data = request.data if request.data else {}
        serializer = ConvertToUSDSerializer(data=data)

        if not serializer.is_valid():
            return Response(data={'message': 'BadRequest'}, status=400)

        balance_from = convert_currency_to_usdt(serializer.validated_data['type']).get('price')

        if not balance_from:
            return Response(data={'message': 'Internal server error'}, status=500)

        return Response(
            data={'message': 'OK', 'data': {'price': decimal.Decimal(balance_from) * serializer.validated_data['amount']}},
            status=200)


class SwapDefaultView(GenericAPIView):
    serializer_class = ConvertToUSDSerializer

    def post(self, request):
        ratio = GlobalConfig.objects.filter(config_name='SWAP_RATIO').first()
        if not ratio:
            return Response(data={'message': 'Internal server error'}, status=500)
        ratio_value = ratio.config_value

        balance_from = convert_currency_to_usdt(CurrencyType.BTC).get('price')
        balance_to = convert_currency_to_usdt(CurrencyType.ETH).get('price')
        if not balance_from or not balance_to:
            return Response(data={'message': 'Internal server error'}, status=500)

        ratio_balance = (balance_from / balance_to) * (ratio_value / 100)
        data = {
            'from_type': CurrencyType.BTC,
            'to_type': CurrencyType.ETH,
            'from_amount': 1,
            'ratio': ratio_value,
            'ratio_balance': ratio_balance,
            'to_amount': (balance_from / balance_to) * ((100 - ratio_value) / 100),
        }

        return Response(data={'message': 'OK', 'data': data}, status=200)


class FirstStepSwapView(GenericAPIView):
    permission_classes = [IsAuthenticatedPanc]
    serializer_class = SwapSerializer

    def get(self, request):
        amount = float(request.GET.get("amount", ""))
        currency_type = "ETH"
        url = "https://min-api.cryptocompare.com/data/price?fsym=" + f"{currency_type}" + "&tsyms=BTC,USD,EUR"
        try:
            res = requests.get(url=url, headers={'X-Api-Key': settings.API_KEY})
            if res.status_code == 200:
                res = res.json()
                global usd
                usd = res.get("USD", "")
        except:
            return Response({"message": "please check again later"})
        total = usd * amount
        data = {
            "total": total,
            "usd": usd
        }
        mumbai_rpc_url = "https://rpc-mumbai.maticvigil.com"
        web3 = Web3(Web3.HTTPProvider(mumbai_rpc_url))
        connect = web3.is_connected()
        print(web3)
        if not connect:
            return Response(status=500)
        # user_wallet_balance = web3.eth.get_balance(request.user.wallet_address)
        user_wallet_balance = web3.eth.get_balance("0x8690F1feff62008A396B31c2C3f380bD0Ca6d8b8")  # TEST
        print(user_wallet_balance)
        if user_wallet_balance < amount:
            return Response({"message": "YOUR BALANCE IS NOT ENOUGH IN WALLET"})
        with transaction.atomic():
            transaction_user = Transaction.objects.create(
                amount=amount,
                amount_swap=usd,
                wallet=Wallet.objects.get(identifier=request.user.wallet_address),
                currency_type=currency_type,
                currency_swap="USD",
                is_swap=True
            )
            transaction_log_user = TransactionLog.objects.create(
                wallet=Wallet.objects.get(identifier=request.user.wallet_address),
                amount=amount
            )
        return Response(data)

class SecondStepSwapView(GenericAPIView):
    permission_classes = [IsAuthenticatedPanc]
    serializer_class = SecondSwapSerializer

    def post(self, request):
        data = request.data if request.data else {}
        serializer = SecondSwapSerializer(data=data)

        if not serializer.is_valid():
            return Response(data={'message': 'BadRequest'}, status=400)
        user_id = request.user_id
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(data={'message': 'Internal server error'}, status=500)
        wallet_address = Wallet.objects.get(identifier=user.wallet_address)
        with transaction.atomic():
            payment_to_main_wallet = Wallet.objects.select_for_update().get(wallet_type=WalletType.MAIN)
            payment_to_main_wallet.balance += serializer.validated_data['ratio_balance']
            payment_to_main_wallet.save()
            transaction_user = Transaction.objects.create(
                amount=serializer.validated_data['from_amount'],
                amount_swap=serializer.validated_data['to_amount'],
                wallet=wallet_address,
                currency_type=serializer.validated_data['from_type'],
                currency_swap=serializer.validated_data['to_type'],
                is_swap=True
            )
            transaction_log_user = TransactionLog.objects.create(
                wallet=wallet_address,
                amount=serializer.validated_data['from_amount']
            )
            transaction_site = Transaction.objects.create(
                amount=serializer.validated_data['to_amount'],
                amount_swap=serializer.validated_data['from_amount'],
                wallet=payment_to_main_wallet,
                currency_type=serializer.validated_data['to_type'],
                currency_swap=serializer.validated_data['from_type'],
                is_swap=True
            )
            transaction_log_site = TransactionLog.objects.create(
                wallet=payment_to_main_wallet,
                amount=serializer.validated_data['to_amount']
            )
        return Response(data={'message': 'Your transaction is done'}, status=200)


class CashoutListView(GenericAPIView):
    permission_classes = [IsAuthenticatedPanc]
    serializer_class = CashoutRequestSerializer

    def get(self, request):
        user_id = request.user_id
        user = User.objects.filter(id=user_id).first()
        wallet_qs = Wallet.objects.filter(identifier=user.wallet_address, wallet_type=WalletType.USD)
        if len(wallet_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        wallet_obj = wallet_qs.first()

        cashout_request_qs = CashOutRequest.objects.filter(wallet=wallet_obj).order_by('-created_at')
        data = []

        for cashout_request in cashout_request_qs:
            data.append({
                'type': cashout_request.type,
                'amount': cashout_request.amount,
                'status': cashout_request.get_status_dict(),
                'description': cashout_request.description,
                'canceled_at': cashout_request.canceled_at,
                'reserved_at': cashout_request.reserved_at,
                'processed_at': cashout_request.processed_at,
                'updated_at': cashout_request.updated_at,
                'created_at': cashout_request.created_at
            })

        return Response(data={'message': 'OK', 'data': data}, status=200)


class CashoutDetailView(GenericAPIView):
    permission_classes = [IsAuthenticatedPanc]
    serializer_class = CashoutRequestSerializer

    def get(self, request, pk):
        user_id = request.user_id
        user = User.objects.filter(id=user_id).first()
        wallet_qs = Wallet.objects.filter(identifier=user.wallet_address, wallet_type=WalletType.USD)
        if len(wallet_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        wallet_obj = wallet_qs.first()

        cashout_request_obj = CashOutRequest.objects.filter(id=pk, wallet=wallet_obj).first()

        if not cashout_request_obj:
            return Response(data={'message': 'Not found'}, status=404)

        data = {
            'type': cashout_request_obj.type,
            'amount': cashout_request_obj.amount,
            'status': cashout_request_obj.get_status_dict(),
            'description': cashout_request_obj.description,
            'canceled_at': cashout_request_obj.canceled_at,
            'reserved_at': cashout_request_obj.reserved_at,
            'processed_at': cashout_request_obj.processed_at,
            'updated_at': cashout_request_obj.updated_at,
            'created_at': cashout_request_obj.created_at
        }

        return Response(data={'message': 'OK', 'data': data}, status=200)

    def post(self, request):
        data = request.data if request.data else {}
        serializer = CashoutRequestSerializer(data=data)

        if not serializer.is_valid():
            return Response(data={'message': 'BadRequest'}, status=400)

        user_id = request.user_id
        user = User.objects.filter(id=user_id).first()
        wallet_qs = Wallet.objects.filter(identifier=user.wallet_address, wallet_type=WalletType.USD)
        if len(wallet_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        wallet_obj = wallet_qs.first()

        balance_from_usd = convert_currency_to_usdt(serializer.validated_data['type']).get('price')

        if not balance_from_usd:
            return Response(data={'message': 'Internal server error'}, status=500)

        balance_usd = balance_from_usd * serializer.validated_data['amount']

        if wallet_obj.balance < balance_usd:
            return Response(data={'message': 'Bad request'}, status=400)

        cashout_request_obj = CashOutRequest.objects.create(wallet=wallet_obj, type=serializer.validated_data['type'],
                                                            amount=serializer.validated_data['amount'])

        data = {
            'type': cashout_request_obj.type,
            'amount': cashout_request_obj.amount,
            'status': cashout_request_obj.get_status_dict(),
            'description': cashout_request_obj.description,
            'updated_at': cashout_request_obj.updated_at,
            'created_at': cashout_request_obj.created_at
        }

        return Response(data={'message': 'OK', 'data': data}, status=200)


class TransactionLogListView(GenericAPIView):
    permission_classes = [IsAuthenticatedPanc]

    def get(self, request):
        user_id = request.user_id
        user = User.objects.filter(id=user_id).first()
        wallet_qs = Wallet.objects.filter(identifier=user.wallet_address, wallet_type=WalletType.USD)
        if len(wallet_qs) != 1:
            return Response(data={'message': 'BadRequest'}, status=400)

        wallet_obj = wallet_qs.first()

        transaction_log_qs = TransactionLog.objects.filter(wallet=wallet_obj).order_by('-created_at')
        data = []
        for transaction_log in transaction_log_qs:
            data.append({
                'amount': transaction_log.amount,
                'temp_transaction_ref': transaction_log.temp_transaction_ref,
                'transaction_type': transaction_log.transaction_type,
                'created_at': transaction_log.created_at
            })

        return Response(data={'message': 'OK', 'data': data}, status=200)

# class TransactionView(GenericAPIView):
#     permission_classes = [IsAuthenticatedPanc]
#     serializer_class = SwapSerializer
#
#     def post(self, request):
#         coin_from = request.data.get("coin_from", "")
#         coin_to = request.data.get("coin_to", "")
#         # check coins price
#         key_1 = "https://api.binance.com/api/v3/ticker/price?symbol=" + coin_from
#         key_2 = "https://api.binance.com/api/v3/ticker/price?symbol=" + coin_to
#
#         coin_from_price = (requests.get(key_1)).json()
#         coin_to_price = (requests.get(key_2)).json()
#
#         coin_from_count = int(request.data.get("coin_from_count", ""))
#         coin_to_count = int(request.data.get("coin_to_count", ""))
#
#         result_coin_from_price = coin_from_count * coin_from_price
#         result_coin_to_price = coin_to_count * coin_to_price
#
#         if result_coin_to_price > result_coin_from_price:
#             # check user wallet balance
#             user_wallet_balance = Web3.eth.get_balance(request.user.wallet_address)
#             if (user_wallet_balance + result_coin_from_price) > result_coin_to_price:
#                 raise Exception("YOUR BALANCE IS NOT ENOUGH")
#         # TODO CHECK coin_to_count
