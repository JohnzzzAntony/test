"""
Django 5.x compatibility fix for django-cloudinary-storage.

django-cloudinary-storage overrides Django's built-in collectstatic command
and reads `settings.STATICFILES_STORAGE` on line 27 of its collectstatic.py:

    if (settings.STATICFILES_STORAGE == 'cloudinary_storage.storage.StaticCloudinaryStorage' ...

Django 5.x removed STATICFILES_STORAGE (replaced by STORAGES dict), so this
crashes with:
    AttributeError: 'Settings' object has no attribute 'STATICFILES_STORAGE'

We don't use Cloudinary for STATIC files (we use WhiteNoise). Static storage
is configured via STORAGES["staticfiles"]. Cloudinary is only used for MEDIA
(user uploads) via STORAGES["default"].

This command shadows cloudinary_storage's broken collectstatic by using the
standard Django staticfiles collectstatic directly. Django picks the management
command from the LAST matching app in INSTALLED_APPS, so 'core' (which comes
after 'cloudinary_storage') wins.
"""

from django.contrib.staticfiles.management.commands.collectstatic import (
    Command,  # noqa: F401 — re-exported so Django discovers it
)
