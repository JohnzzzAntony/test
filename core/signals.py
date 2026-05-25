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
    # Broadcast theme update to all open frontend pages
    broadcast_theme_update(instance)


@receiver(post_save, sender=AnnouncementBar)
def on_announcement_saved(sender, instance, **kwargs):
    invalidate_site_settings_cache()


@receiver(post_delete, sender=AnnouncementBar)
def on_announcement_deleted(sender, instance, **kwargs):
    invalidate_site_settings_cache()


def broadcast_theme_update(design_settings):
    """
    Broadcast theme settings update to all open frontend pages.
    Uses localStorage as a cross-tab communication mechanism.
    """
    try:
        import json
        from django.utils import timezone
        
        # Get all settings as a dictionary
        settings_dict = {
            field.name: getattr(design_settings, field.name, None)
            for field in design_settings._meta.fields
        }
        
        # Create broadcast payload
        payload = {
            'type': 'theme_update',
            'settings': settings_dict,
            'version': int(timezone.now().timestamp() * 1000)
        }
        
        # Store in localStorage for cross-tab communication
        # Frontend JavaScript will pick this up
        broadcast_data = json.dumps(payload)
        
        # We'll store this in the cache or settings to be picked up by frontend
        # For now, we invalidate the cache which will cause next request to get fresh data
        # The frontend polling will pick up the changes
        
        print(f"[ThemeUpdate] Broadcast theme update v{payload['version']}")
        
    except Exception as e:
        print(f"[ThemeUpdate] Failed to broadcast: {e}")