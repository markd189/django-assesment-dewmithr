"""!@file admin.py
@brief Django admin configuration.

Admin UI is configured with a simple role model:
- Superuser: full access.
- Staff (non-superuser): restricted to their own devices, telemetry, rules, and alerts.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Device, Telemetry, AlertRule, Alert


# -------------------------
# Device Admin
# -------------------------
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """!@brief Django admin configuration for Device."""

    list_display = ("name", "device_id", "type", "location", "owner", "is_active")
    readonly_fields = ("device_id", "created_at", "owner")

    def get_queryset(self, request):
        """!@brief Filter device list to owned devices for non-superusers."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        """!@brief Set owner on create; prevent staff from assigning devices to others."""
        if not change:  # assign owner only when creating
            obj.owner = request.user
        obj.save()

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """!@brief Restrict the owner dropdown for non-superusers."""
        if not request.user.is_superuser and db_field.name == "owner":
            kwargs["queryset"] = get_user_model().objects.filter(pk=request.user.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# -------------------------
# Telemetry Admin
# -------------------------
@admin.register(Telemetry)
class TelemetryAdmin(admin.ModelAdmin):
    """!@brief Django admin configuration for Telemetry."""

    list_display = ("device", "status", "cpu", "memory", "temperature", "timestamp")

    def get_queryset(self, request):
        """!@brief Filter telemetry list to owned devices for non-superusers."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(device__owner=request.user)

    def has_add_permission(self, request):
        """!@brief Only superusers can manually add telemetry in admin."""
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """!@brief Only superusers can delete telemetry."""
        return request.user.is_superuser

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """!@brief Restrict device dropdown for non-superusers."""
        if not request.user.is_superuser and db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# -------------------------
# AlertRule Admin
# -------------------------
@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    """!@brief Django admin configuration for AlertRule."""

    list_display = ("device", "rule_type", "threshold", "severity", "is_active")

    def get_queryset(self, request):
        """!@brief Filter alert rule list to owned devices for non-superusers."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(device__owner=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """!@brief Restrict device dropdown for non-superusers."""
        if not request.user.is_superuser and db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# -------------------------
# Alert Admin
# -------------------------
@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """!@brief Django admin configuration for Alert."""

    list_display = ("device", "message", "severity", "state", "triggered_at")
    list_filter = ("state", "severity", "device")
    actions = ["acknowledge_alerts"]

    def get_queryset(self, request):
        """!@brief Filter alert list to owned devices for non-superusers."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(device__owner=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """!@brief Restrict device/rule dropdowns for non-superusers."""
        if not request.user.is_superuser and db_field.name == "device":
            kwargs["queryset"] = Device.objects.filter(owner=request.user)
        if not request.user.is_superuser and db_field.name == "rule":
            kwargs["queryset"] = AlertRule.objects.filter(device__owner=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def acknowledge_alerts(self, request, queryset):
        """!@brief Admin action to acknowledge selected alerts."""
        queryset.update(state="ACK", acknowledged_at=timezone.now())

    acknowledge_alerts.short_description = "Mark selected alerts as Acknowledged"