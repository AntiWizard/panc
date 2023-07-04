from django.urls import path

from user.views import VerifyLoginView, LogoutView, RefreshTokenView

urlpatterns = [
    path('verify-login/', VerifyLoginView.as_view(), name='verify_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh-token/', RefreshTokenView.as_view(), name='refresh_token'),
]
