"""!@file serializers.py
 @brief DRF serializers for the device monitoring API.

 Serializers define the request/response payloads for API endpoints.
 """
from rest_framework import serializers
from .models import Device, Telemetry


class DeviceSerializer(serializers.ModelSerializer):
    """!@brief Serializer for the Device model."""

    class Meta:
        model = Device
        fields = "__all__"
        read_only_fields = ["owner", "device_id", "created_at"]


class TelemetryCreateSerializer(serializers.Serializer):
    """!@brief Serializer for telemetry ingestion.

    Expected input includes the external `device_id` UUID and telemetry metrics.
    """

    device_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=Telemetry.STATUS_CHOICES)
    cpu = serializers.FloatField()
    memory = serializers.FloatField()
    temperature = serializers.FloatField(required=False)

    def create(self, validated_data):
        """!@brief Create a Telemetry record.

        @param validated_data Validated serializer payload.
        @return Newly created Telemetry instance.
        @throws serializers.ValidationError If the device_id is invalid.
        """

        device_id = validated_data.pop("device_id")

        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Invalid device_id")

        return Telemetry.objects.create(device=device, **validated_data)