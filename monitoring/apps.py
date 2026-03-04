"""!@file apps.py
@brief Django application configuration for the monitoring app.

The AppConfig `ready()` hook imports `monitoring.services` to ensure Django
signal receivers are registered at startup.
"""

from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    """!@brief AppConfig for the monitoring application."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'monitoring'

    def ready(self):
        """!@brief Initialize application hooks.

        Importing `monitoring.services` registers telemetry post_save signal
        handlers for alert evaluation.
        """

        import monitoring.services
