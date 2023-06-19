from django.urls import path

from user.views import verify_login, logout

urlpatterns = [
    path('verify-login/', verify_login, name='verify_login'),
    path('logout/', logout, name='logout'),
]
