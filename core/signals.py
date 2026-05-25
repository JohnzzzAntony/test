from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import SiteSettings, AnnouncementBar
from .design_models import DesignSettings
from .context_processors import invalidate_site_settings_cache


@receiver(post_save, sender=SiteSettings)
def on_site_settings_saved(sender, instance, **kwargs):
    invalidate_site_settings_cache()


@receiver(post_save, sender=DesignSettings)
def on_design_settings_saved(sender, instance, **kwargs):
    invalidate_site_settings_cache()


@receiver(post_save, sender=AnnouncementBar)
def on_announcement_saved(sender, instance, **kwargs):
    invalidate_site_settings_cache()


@receiver(post_delete, sender=AnnouncementBar)
def on_announcement_deleted(sender, instance, **kwargs):
    invalidate_site_settings_cache()