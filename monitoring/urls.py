from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, TelemetryCreateView

router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')

urlpatterns = [
    path('', include(router.urls)),
    path("telemetry/", TelemetryCreateView.as_view(), name="telemetry-create"),
]