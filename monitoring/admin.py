from django.contrib import admin
from .models import Device, Telemetry, AlertRule, Alert

# -------------------------
# Device Admin
# -------------------------
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "device_id", "type", "location", "owner", "is_active")
    readonly_fields = ("device_id", "created_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # assign owner only when creating
            obj.owner = request.user
        obj.save()


# -------------------------
# Telemetry Admin
# -------------------------
@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    list_display = ("device", "status", "cpu", "memory", "temperature", "timestamp")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(device__owner=request.user)


# -------------------------
# AlertRule Admin
# -------------------------
@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ("device", "rule_type", "threshold", "severity", "is_active")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(device__owner=request.user)


# -------------------------
# Alert Admin
# -------------------------
@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("device", "message", "severity", "state", "triggered_at")
    list_filter = ("state", "severity", "device")
    actions = ["acknowledge_alerts"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(device__owner=request.user)

    def acknowledge_alerts(self, request, queryset):
        queryset.update(state="ACK", acknowledged_at=None)  # optionally set timestamp
    acknowledge_alerts.short_description = "Mark selected alerts as Acknowledged"