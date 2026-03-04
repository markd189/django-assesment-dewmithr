import uuid
from django.db import models
from django.contrib.auth.models import User


# -------------------------
# DEVICE MODEL
# -------------------------
class Device(models.Model):
    DEVICE_TYPES = [
        ("SENSOR", "Sensor"),
        ("CAMERA", "Camera"),
        ("KIOSK", "Kiosk"),
    ]

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    device_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="devices"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.device_id})"


# -------------------------
# TELEMETRY MODEL
# -------------------------
class Telemetry(models.Model):
    STATUS_CHOICES = [
        ("ONLINE", "Online"),
        ("OFFLINE", "Offline"),
        ("DEGRADED", "Degraded"),
    ]

    id = models.BigAutoField(primary_key=True)
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="telemetry",
        db_index=True
    )

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    cpu = models.FloatField()
    memory = models.FloatField()
    temperature = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.device.name} - {self.timestamp}"


# -------------------------
# ALERT RULE MODEL
# -------------------------
class AlertRule(models.Model):
    RULE_TYPES = [
        ("CPU_HIGH", "CPU High"),
        ("MEMORY_HIGH", "Memory High"),
        ("TEMP_HIGH", "Temperature High"),
        ("OFFLINE", "Device Offline"),
    ]

    id = models.BigAutoField(primary_key=True)

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="alert_rules"
    )

    rule_type = models.CharField(max_length=30, choices=RULE_TYPES)
    threshold = models.FloatField(blank=True, null=True)

    severity = models.CharField(
        max_length=10,
        choices=[
            ("LOW", "Low"),
            ("MEDIUM", "Medium"),
            ("HIGH", "High"),
        ],
        default="MEDIUM"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device.name} - {self.rule_type}"


# -------------------------
# ALERT MODEL
# -------------------------
class Alert(models.Model):
    STATE_CHOICES = [
        ("OPEN", "Open"),
        ("ACK", "Acknowledged"),
        ("RESOLVED", "Resolved"),
    ]

    id = models.BigAutoField(primary_key=True)

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="alerts"
    )

    rule = models.ForeignKey(
        AlertRule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alerts"
    )

    message = models.TextField()
    severity = models.CharField(max_length=10)
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default="OPEN"
    )

    triggered_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Alert for {self.device.name} - {self.state}"