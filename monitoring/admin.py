from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Device, Telemetry, AlertRule, Alert

# -------------------------
# Device Admin
# -------------------------
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "device_id", "type", "location", "owner", "is_active")
    readonly_fields = ("device_id", "created_at", "owner")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not change:  # assign owner only when creating
            obj.owner = request.user
        obj.save()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "owner":
            kwargs["queryset"] = get_user_model().objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(owner=request.user)
        if not request.user.is_superuser and db_field.name == "rule":
            kwargs["queryset"] = AlertRule.objects.filter(device__owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def acknowledge_alerts(self, request, queryset):
        queryset.update(state="ACK", acknowledged_at=timezone.now())
    acknowledge_alerts.short_description = "Mark selected alerts as Acknowledged"