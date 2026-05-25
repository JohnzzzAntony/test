from django.core.management.base import BaseCommand
from core.context_processors import invalidate_site_settings_cache


class Command(BaseCommand):
    help = "Clear the cached site settings (DesignSettings, SiteSettings, Announcements)"

    def handle(self, *args, **options):
        invalidate_site_settings_cache()
        self.stdout.write(self.style.SUCCESS("Site settings cache cleared successfully."))