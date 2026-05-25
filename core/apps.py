from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = '⚙️ Settings'

    def ready(self):
        # Import signals to register them (cache invalidation on settings save)
        from . import signals  # noqa: F401
