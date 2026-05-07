from core.models import SiteSettings
settings = SiteSettings.objects.first()
if not settings:
    settings = SiteSettings.objects.create(site_name="JKR International", enable_email_notifications=True)
    print("Created new SiteSettings.")
else:
    print(f"Existing Settings: {settings.site_name}")
    print(f"Email Enabled: {settings.enable_email_notifications}")
    if not settings.enable_email_notifications:
        settings.enable_email_notifications = True
        settings.save()
        print("Enabled email notifications.")
