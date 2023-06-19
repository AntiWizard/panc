from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('user.urls')),
    path('lottery/', include('lottery.urls')),
    path('wallet/', include('wallet.urls')),
]
