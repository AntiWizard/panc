from django.urls import path

from user.views import verify_login, logout, refresh_token

urlpatterns = [
    path('verify-login/', verify_login, name='verify_login'),
    path('logout/', logout, name='logout'),
    path('refresh-token/', refresh_token),
]
