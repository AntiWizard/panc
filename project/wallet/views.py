import json
import requests
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
import decimal
from web3 import Web3, EthereumTesterProvider
from user.models import User
from user.permissions import IsAuthenticatedPenc
from utils.ex_request import convert_currency_to_usdt
from wallet.constants import WalletType, CurrencyType
from wallet.models import TransactionLog, Wallet, CashOutRequest, Transaction
from wallet.serializers import CashoutRequestSerializer, SwapSerializer, ConvertToUSDSerializer


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

    def post(self, request):
        balance_from = convert_currency_to_usdt(CurrencyType.BTC).get('price')
        balance_to = convert_currency_to_usdt(CurrencyType.ETH).get('price')

        if not balance_from or not balance_to:
            return Response(data={'message': 'Internal server error'}, status=500)
        data = {
            'from_type': CurrencyType.BTC,
            'to_type': CurrencyType.ETH,
            'from_amount': decimal.Decimal(1),
            'to_amount': decimal.Decimal(balance_from) / decimal.Decimal(balance_to),
        }

        return Response(data={'message': 'OK', 'data': data}, status=200)


class SwapView(GenericAPIView):
    permission_classes = [IsAuthenticatedPenc]
    serializer_class = SwapSerializer

    def post(self, request):
        data = request.data if request.data else {}
        serializer = SwapSerializer(data=data)

        if not serializer.is_valid():
            return Response(data={'message': 'BadRequest'}, status=400)

        user_id = request.user_id
        user = User.objects.filter(id=user_id).first()
        wallet_qs = Wallet.objects.filter(identifier=user.wallet_address, wallet_type=WalletType.USD)
        if len(wallet_qs) != 1:
            return Response(data={'message': 'Internal server error'}, status=500)

        transaction = Transaction.objects.create(amount=serializer.validated_data['amount'],
                                                 type=serializer.validated_data['from_type'],
                                                 currency_swap=serializer.validated_data['to_type'],
                                                 is_swap=True)

        data = {
            'from_type': transaction.currency_type,
            'swap_type': transaction.currency_swap,
            'status': transaction.status,
            'created_at': transaction.created_at
        }

        return Response(data={'message': 'OK', 'data': data}, status=200)


class CashoutListView(GenericAPIView):
    permission_classes = [IsAuthenticatedPenc]

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
    permission_classes = [IsAuthenticatedPenc]
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
    permission_classes = [IsAuthenticatedPenc]

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


class ConnectWalletView(GenericAPIView):

    def get(self, request):
        address = request.GET.get("address")  # get wallet address in param
        result = Web3.is_address(address)
        if result:
            try:
                user = User.objects.get(wallet_address=address, is_active=True)
            except ValueError:
                return Response("THIS_WALLET_EXIST")
            user = User.objects.create(wallet_address=address)
            return Response(json.loads(user))  # TODO CHECK USER AND WALLET MODEL
        return Response("YOUR_WALLET_IS_NOT_VALID")


class TransactionView(GenericAPIView):
    permission_classes = [IsAuthenticatedPenc]
    serializer_class = SwapSerializer

    def post(self, request):
        coin_from = request.data.get("coin_from", "")
        coin_to = request.data.get("coin_to", "")
        # check coins price
        key_1 = "https://api.binance.com/api/v3/ticker/price?symbol=" + coin_from
        key_2 = "https://api.binance.com/api/v3/ticker/price?symbol=" + coin_to

        coin_from_price = (requests.get(key_1)).json()
        coin_to_price = (requests.get(key_2)).json()

        coin_from_count = int(request.data.get("coin_from_count", ""))
        coin_to_count = int(request.data.get("coin_to_count", ""))

        result_coin_from_price = coin_from_count * coin_from_price
        result_coin_to_price = coin_to_count * coin_to_price

        if result_coin_to_price > result_coin_from_price:
            # check user wallet balance
            user_wallet_balance = Web3.eth.get_balance(request.user.wallet_address)
            if (user_wallet_balance + result_coin_from_price) > result_coin_to_price:
                raise Exception("YOUR BALANCE IS NOT ENOUGH")
        #TODO CHECK coin_to_count

