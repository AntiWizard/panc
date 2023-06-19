import jwt
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.functions import generate_new_session_for_user, generate_token_pair_dict
from user.models import UserSession, User
from user.serializers import LogoutSerializer, VerifyLoginSerializer
from wallet.constants import WalletType
from wallet.models import Wallet


@api_view(['POST'])
def verify_login(request):
    data = request.data if request.data else {}
    serializer = VerifyLoginSerializer(data=data)

    if not serializer.is_valid():
        return Response(data={'message': 'Bad request'}, status=400)
    wallet_address = serializer.validated_data['address']
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
        token_data = jwt.decode(serializer.validated_data['access'], settings.PUBLIC_KEY, algorithms=['RS256'],
                                leeway=5)
        if 'type' in token_data.keys() and token_data['type'] == 'access':
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
