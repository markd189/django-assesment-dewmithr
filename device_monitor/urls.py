"""!@file urls.py
@brief Project URL configuration.

Routes:
- /admin/ : Django admin site.
- /api/ : Monitoring API endpoints (see monitoring/urls.py).
- /api/schema/ : OpenAPI schema (drf-spectacular).
- /api/docs/ : Swagger UI (drf-spectacular).
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path('api/', include('monitoring.urls')),
]
