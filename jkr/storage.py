"""
Custom static file storage for Railway/Production deployments.

CKEditor and Jazzmin reference optional vendor files (PNG textures, alternate
skin CSS, etc.) that may not be present in the staticfiles tree.  Django's
ManifestStaticFilesStorage / HashedFilesMixin raises ValueError when it
encounters a url() reference to a missing file while post-processing CSS.

This storage subclass silently falls back to the unhashed original path for
any file that cannot be found, so collectstatic always succeeds.
"""

from whitenoise.storage import ManifestStaticFilesStorage


class CustomWhiteNoiseStorage(ManifestStaticFilesStorage):
    """
    WhiteNoise ManifestStaticFilesStorage with two safety overrides:

    1. manifest_strict = False  – prevents runtime KeyError when a hashed
       filename is missing from the manifest (e.g. admin CSS loaded by third-
       party packages that weren't collected).

    2. hashed_name()  – falls back to the original name instead of raising
       ValueError when a file referenced inside CSS/JS cannot be found on disk.
       This is necessary for CKEditor 4 skin files and Jazzmin vendor assets
       that reference texture PNGs not shipped with the package.
    """

    manifest_strict = False

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content=content, filename=filename)
        except (ValueError, FileNotFoundError):
            # File is referenced in CSS/JS but not present – return as-is
            return name
