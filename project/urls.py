from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('user.urls')),
    path('lottery/', include('lottery.urls')),
    path('wallet/', include('wallet.urls')),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
