from django.contrib import admin
from django.urls import path, include, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from apps.proxy.views import ProxyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.authentication.urls')),

    # Catch-all for API Gateway Proxy
    re_path(r'^api/v1/(?P<service_name>[a-z-]+)(?:/(?P<path>.*))?$', ProxyView.as_view(), name='api-gateway-proxy'),

    # Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Root redirect to Swagger
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='root'),
]
