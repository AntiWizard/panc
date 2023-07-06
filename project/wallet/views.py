import decimal

from django.conf import settings
from django.db import transaction
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from web3 import Web3

from config.models import GlobalConfig
from user.models import User
from user.permissions import IsAuthenticatedPanc
from utils.ex_request import convert_currency_to_usd
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

        balance_from = convert_currency_to_usd(serializer.validated_data['type']).get('USD')

        if not balance_from:
            return Response(data={'message': 'Internal server error'}, status=500)

        return Response(
            data={'message': 'OK',
                  'data': {'price': round(decimal.Decimal(str(balance_from)) * serializer.validated_data['amount'], 10)}},
            status=200)


class CurrencyTypeListView(GenericAPIView):
    def get(self, request):
        data = {}
        for currency, value in CurrencyType.CHOICES:
            data[currency] = value.upper()

        return Response(data={'message': 'OK', 'data': data}, status=200)


class SwapDefaultView(GenericAPIView):

    def post(self, request):
        ratio = GlobalConfig.objects.filter(config_name='SWAP_RATIO').first()
        if not ratio:
            return Response(data={'message': 'Internal server error'}, status=500)
        ratio_value = float(ratio.config_value)

        balance_from = convert_currency_to_usd(CurrencyType.ETH).get('USD')
        balance_to = convert_currency_to_usd(CurrencyType.BTC).get('USD')
        if not balance_from or not balance_to:
            return Response(data={'message': 'Internal server error'}, status=500)

        ratio_balance = round((balance_from / balance_to) * (ratio_value / 100), 10)
        data = {
            'from_type': CurrencyType.ETH,
            'to_type': CurrencyType.BTC,
            'from_amount': 1,
            'ratio': ratio_value,
            'ratio_balance': ratio_balance,
            'to_amount': round((balance_from / balance_to) * ((100 - ratio_value) / 100), 10),
        }

        return Response(data={'message': 'OK', 'data': data}, status=200)


class FirstStepSwapView(GenericAPIView):
    permission_classes = [IsAuthenticatedPanc]
    serializer_class = SwapSerializer

    def post(self, request):
        data = request.data if request.data else {}
        serializer = SwapSerializer(data=data)
        if not serializer.is_valid():
            return Response({'message': 'Bad Request'}, status=400)

        admin_wallet = GlobalConfig.objects.filter(config_name='ADMIN_WALLET', is_active=True).first()
        if not admin_wallet:
            return Response({'message': 'Internal server error'}, status=500)

        user = User.objects.filter(id=request.user_id, is_active=True).first()
        if not user:
            return Response({'message': 'Bad Request'}, status=400)

        from_balance_usd = convert_currency_to_usd(serializer.validated_data['from_type']).get('USD')
        # to_balance_usd = convert_currency_to_usd(serializer.validated_data['to_type']).get('USD')

        infura_key = GlobalConfig.objects.filter(config_name='INFURA_API_KEY', is_active=True).first()
        if not infura_key:
            return Response({'message': 'Internal server error'}, status=500)

        infura_url = f'{settings.INFURA_API}{infura_key.config_value}'
        web3 = Web3(Web3.HTTPProvider(infura_url))

        connect = web3.is_connected()
        if not connect:
            return Response(status=500)

        try:
            check_user_address = web3.to_checksum_address(user.wallet_address)
            user_wallet_balance = web3.eth.get_balance(check_user_address)
        except:
            return Response({'message': 'Bad Request'}, status=500)

        if user_wallet_balance < serializer.validated_data['from_amount']:
            return Response({'message': 'YOUR BALANCE IS NOT ENOUGH IN WALLET'}, status=400)

        # Get the current gas price
        gas_price = web3.eth.gas_price

        # Create a new transaction object with the receiver address as the recipient
        transaction = {
            'to': admin_wallet,
            'value': web3.to_wei(serializer.validated_data['from_amount'], 'ether'),  # 1 ETH in Wei
            'gas': 21000,
            'gasPrice': gas_price,
            'nonce': web3.eth.get_transaction('0x' + user.wallet_address)
        }
        # Sign the transaction with your private key
        signed_tx = web3.eth.account.sign_transaction(transaction, 'YOUR_PRIVATE_KEY')  # TODO GET PRIVATE KEY FROM ADMIN
        # Send tx and wait for receipt
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        data = {}
        Transaction.objects.create(
            amount=serializer.validated_data['from_amount'],
            amount_swap=from_balance_usd,
            wallet=Wallet.objects.get(identifier=request.user.wallet_address),
            currency_type=serializer.validated_data['to_type'],
            currency_swap=CurrencyType.USD,
            is_swap=True
        )
        TransactionLog.objects.create(
            wallet=user.wallet_address,
            amount=serializer.validated_data['from_type']
        )
        data['tx'] = {
            'from': user.wallet_address, 'to': admin_wallet,
            'amount': web3.to_wei(serializer.validated_data['from_amount'], 'ether'),
            'confirm': tx_receipt.transactionHash.hex()
        }

        return Response(data={'message': 'OK', 'data': data}, status=200)


# class SecondStepSwapView(GenericAPIView):
#     permission_classes = [IsAuthenticatedPanc]
#     serializer_class = SecondSwapSerializer
#
#     def post(self, request):
#         data = request.data if request.data else {}
#         serializer = SecondSwapSerializer(data=data)
#
#         if not serializer.is_valid():
#             return Response(data={'message': 'BadRequest'}, status=400)
#         user_id = request.user_id
#         user = User.objects.filter(id=user_id).first()
#         if not user:
#             return Response(data={'message': 'Internal server error'}, status=500)
#         wallet_address = Wallet.objects.get(identifier=user.wallet_address)
#         with transaction.atomic():
#             payment_to_main_wallet = Wallet.objects.select_for_update().get(wallet_type=WalletType.MAIN)
#             payment_to_main_wallet.balance += serializer.validated_data['ratio_balance']
#             payment_to_main_wallet.save()
#             transaction_user = Transaction.objects.create(
#                 amount=serializer.validated_data['from_amount'],
#                 amount_swap=serializer.validated_data['to_amount'],
#                 wallet=wallet_address,
#                 currency_type=serializer.validated_data['from_type'],
#                 currency_swap=serializer.validated_data['to_type'],
#                 is_swap=True
#             )
#             transaction_log_user = TransactionLog.objects.create(
#                 wallet=wallet_address,
#                 amount=serializer.validated_data['from_amount']
#             )
#             transaction_site = Transaction.objects.create(
#                 amount=serializer.validated_data['to_amount'],
#                 amount_swap=serializer.validated_data['from_amount'],
#                 wallet=payment_to_main_wallet,
#                 currency_type=serializer.validated_data['to_type'],
#                 currency_swap=serializer.validated_data['from_type'],
#                 is_swap=True
#             )
#             transaction_log_site = TransactionLog.objects.create(
#                 wallet=payment_to_main_wallet,
#                 amount=serializer.validated_data['to_amount']
#             )
#         return Response(data={'message': 'Your transaction is done'}, status=200)


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

        balance_from_usd = convert_currency_to_usd(serializer.validated_data['type']).get('USD')

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
