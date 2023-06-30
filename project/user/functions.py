import random
import string
from time import time

import jwt
from django.conf import settings

from user.models import UserSession


def generate_random_session_string():
    ret = ''
    for _ in range(10):
        ret += random.choice(string.ascii_uppercase + string.digits)
    return ret


def generate_new_session_for_user(user_object):
    while True:
        session_id = generate_random_session_string()
        if len(UserSession.objects.filter(session_id=session_id)) == 0:
            UserSession.objects.create(session_id=session_id, user=user_object)
            return session_id


def generate_secure_token(data):
    token = jwt.encode(data, settings.PRIVATE_KEY, algorithm='RS256')
    return token


def generate_token_pair_dict(user_id, session_id):
    access_dict = {
        'type': 'access',
        'exp': round(time() + settings.ACCESS_TOKEN_EXP_SECONDS),
        'user_id': user_id,
        'session_id': session_id,
    }
    refresh_dict = {
        'type': 'refresh',
        'exp': round(time() + settings.REFRESH_TOKEN_EXP_SECONDS),
        'user_id': user_id,
        'session_id': session_id
    }
    return {'access': generate_secure_token(access_dict), 'refresh': generate_secure_token(refresh_dict)}
