"""!@file services.py
@brief Domain services for telemetry processing and alert generation.

This module hooks into Telemetry creation and evaluates active AlertRules
to generate Alerts.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Telemetry, AlertRule, Alert


@receiver(post_save, sender=Telemetry)
def check_alert_rules(sender, instance, created, **kwargs):
    """!@brief Signal receiver for newly created telemetry.

    @param sender Model class.
    @param instance Telemetry instance.
    @param created Whether the object was created.
    @param kwargs Additional signal args.
    """

    if not created:
        return  # only trigger on new telemetry

    device = instance.device
    rules = AlertRule.objects.filter(device=device, is_active=True)

    for rule in rules:

        # CPU HIGH
        if rule.rule_type == "CPU_HIGH" and rule.threshold is not None:
            if instance.cpu > rule.threshold:
                create_alert(device, rule, f"CPU usage exceeded {rule.threshold}%")

        # MEMORY HIGH
        elif rule.rule_type == "MEMORY_HIGH" and rule.threshold is not None:
            if instance.memory > rule.threshold:
                create_alert(device, rule, f"Memory usage exceeded {rule.threshold}%")

        # TEMP HIGH
        elif rule.rule_type == "TEMP_HIGH" and rule.threshold is not None:
            if instance.temperature and instance.temperature > rule.threshold:
                create_alert(device, rule, f"Temperature exceeded {rule.threshold}°C")

        # OFFLINE
        elif rule.rule_type == "OFFLINE":
            if instance.status == "OFFLINE":
                create_alert(device, rule, "Device went offline")


def create_alert(device, rule, message):
    """!@brief Create an alert if there is no existing OPEN alert for the same rule.

    This prevents repeated alerts while an issue is still open.

    @param device Device instance.
    @param rule AlertRule instance.
    @param message Human-readable alert message.
    """

    if Alert.objects.filter(device=device, rule=rule, state="OPEN").exists():
        return

    Alert.objects.create(
        device=device,
        rule=rule,
        message=message,
        severity=rule.severity,
        state="OPEN",
    )