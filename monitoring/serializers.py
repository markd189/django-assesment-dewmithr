from rest_framework import serializers
from .models import Device, Telemetry


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields = "__all__"
        read_only_fields = ["owner", "device_id", "created_at"]


class TelemetryCreateSerializer(serializers.Serializer):
    device_id = serializers.UUIDField()
    status = serializers.ChoiceField(choices=Telemetry.STATUS_CHOICES)
    cpu = serializers.FloatField()
    memory = serializers.FloatField()
    temperature = serializers.FloatField(required=False)

    def create(self, validated_data):
        device_id = validated_data.pop("device_id")

        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            raise serializers.ValidationError("Invalid device_id")

        return Telemetry.objects.create(device=device, **validated_data)