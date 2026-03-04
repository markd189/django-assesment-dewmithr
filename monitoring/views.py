"""!@file views.py
@brief DRF views for device CRUD and telemetry ingestion.

This module exposes:
- DeviceViewSet: authenticated CRUD for user-owned devices.
- TelemetryCreateView: telemetry ingestion endpoint.
"""

from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Device
from .serializers import DeviceSerializer, TelemetryCreateSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """!@brief CRUD API for Device objects.

    Non-superusers only operate on devices they own.
    """

    serializer_class = DeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """!@brief Return queryset filtered by the requesting user.

        @return QuerySet of Device objects.
        """

        user = self.request.user
        if user.is_superuser:
            return Device.objects.all()
        return Device.objects.filter(owner=user)

    def perform_create(self, serializer):
        """!@brief Assign the requesting user as owner on create.

        @param serializer Device serializer.
        """

        serializer.save(owner=self.request.user)


class TelemetryCreateView(APIView):
    """!@brief Telemetry ingestion endpoint.

    Accepts the external `device_id` UUID and creates a Telemetry record.
    """

    def post(self, request):
        """!@brief Accept telemetry payload and persist.

        @param request DRF request.
        @return DRF Response.
        """

        serializer = TelemetryCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Telemetry received"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)