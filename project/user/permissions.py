import jwt
from django.conf import settings
from rest_framework import permissions


class IsAuthenticatedPanc(permissions.BasePermission):

    def has_permission(self, request, view):
        if 'HTTP_AUTHORIZATION' not in request.META:
            return False
        auth_token = request.META['HTTP_AUTHORIZATION']
        try:
            token_data = jwt.decode(auth_token, settings.PUBLIC_KEY, algorithms=['RS256'], leeway=5)
            if 'type' in token_data.keys() and token_data['type'] == 'access':
                request.user_id = token_data['user_id']
                request.session_id = token_data['session_id']

                return True
            return False
        except:
            return False
