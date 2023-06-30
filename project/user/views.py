from datetime import timedelta

import jwt
from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from web3 import Web3

from error_code import GENERAL_VALIDATION_ERROR, USER_SUSPENDED
from user.functions import generate_new_session_for_user, generate_token_pair_dict
from user.models import UserSession, User
from user.serializers import LogoutSerializer, VerifyLoginSerializer, TokenRefreshSerializer
from wallet.constants import WalletType
from wallet.models import Wallet


@api_view(['POST'])
def verify_login(request):
    data = request.data if request.data else {}
    serializer = VerifyLoginSerializer(data=data)

    if not serializer.is_valid():
        return Response(data={'message': 'Bad request'}, status=400)
    wallet_address = serializer.validated_data['address']
    result = Web3.is_address(wallet_address)
    if not result:
        return Response(data={'message': 'Bad request'}, status=400)

    user_qs = User.objects.filter(wallet_address=wallet_address)
    if len(user_qs) < 1:
        user = User.objects.create(wallet_address=wallet_address)
        wallet = Wallet.objects.create(identifier=wallet_address, wallet_type=WalletType.USD)
    else:
        user = user_qs.first()
        if not user.is_active:
            return Response(data={'message': 'Bad Request'}, status=400)

        wallet_qs = Wallet.objects.filter(identifier=user.wallet_address)
        if len(wallet_qs) != 1:
            return Response(data={'message': 'Bad Request'}, status=400)
        wallet = wallet_qs.first()

    # generate session
    session_id = generate_new_session_for_user(user_object=user)

    token_dict = generate_token_pair_dict(user_id=str(user.id), session_id=session_id)

    user_data = {
        'user_id': str(user.id),
        'wallet_address': user.wallet_address,
        'wallet_balance': wallet.balance
    }

    return Response(data={'message': 'OK', 'token_pair': token_dict, 'user': user_data}, status=200)


@api_view(['POST'])
def logout(request):
    data = request.data if request.data else {}
    serializer = LogoutSerializer(data=data)

    if not serializer.is_valid():
        return Response(data={'message': 'Bad request'}, status=400)

    try:
        token_data = jwt.decode(serializer.validated_data['refresh'], settings.PUBLIC_KEY, algorithms=['RS256'],
                                leeway=5)
        if 'type' in token_data.keys() and token_data['type'] == 'refresh':
            session_id = token_data['session_id']

            session_query_res = UserSession.objects.filter(session_id=session_id, is_active=True)
            if len(session_query_res) != 1:
                return Response(data={'message': 'Not found'}, status=404)

            session_object = session_query_res.first()
            session_object.is_active = False
            session_object.save()

            return Response(data={'message': 'OK'}, status=200)
    except:
        return Response(data={'message': 'Forbidden'}, status=403)


@api_view(['POST'])
def refresh_token(request):
    data = request.data if request.data else {}
    serializer = TokenRefreshSerializer(data=data)

    if not serializer.is_valid():
        return Response(data={'message': 'Bad request', 'error': GENERAL_VALIDATION_ERROR}, status=400)
    try:
        token_data = jwt.decode(serializer.validated_data['refresh'], settings.PUBLIC_KEY, algorithms=['RS256'],
                                leeway=5)
        if 'type' in token_data.keys() and token_data['type'] == 'refresh':
            # check session_id
            session_id = token_data['session_id']

            user_session = UserSession.objects.filter(session_id=session_id, is_active=True).first()

            if user_session is None:
                return Response(data={'message': 'Forbidden'}, status=403)

            user_query_res = User.objects.filter(pk=token_data['user_id'])

            # something is wrong here!
            if len(user_query_res) != 1:
                return Response(data={'message': 'Internal server error'}, status=500)

            user_object = user_query_res.first()

            if not user_object.is_active:
                return Response(data={'message': 'Forbidden', 'error': USER_SUSPENDED}, status=403)

            token_dict = generate_token_pair_dict(user_id=str(user_object.id), session_id=session_id)

            if user_session.last_login < timezone.now() - timedelta(hours=1):
                user_session.last_login = timezone.now()
                user_session.save()

            return Response(data={'message': 'OK', 'token_pair': token_dict}, status=200)
        else:
            return Response(data={'message': 'Forbidden'}, status=403)
    except:
        return Response(data={'message': 'Forbidden'}, status=403)
