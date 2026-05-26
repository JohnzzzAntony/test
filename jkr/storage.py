"""
Custom static file storage for Railway/Production deployments.

CKEditor and Jazzmin reference optional vendor files (PNG textures, alternate
skin CSS, etc.) that may not be present in the staticfiles tree.  Django's
ManifestStaticFilesStorage / HashedFilesMixin raises ValueError when it
encounters a url() reference to a missing file while post-processing CSS, and
raises FileNotFoundError when WhiteNoise tries to open a file that was
referenced but never collected (e.g. CKEditor codesnippet/highlight styles).

This storage subclass silently skips or falls back for any file that cannot be
found, so collectstatic always succeeds.
"""

import logging

from whitenoise.storage import ManifestStaticFilesStorage

logger = logging.getLogger(__name__)


class CustomWhiteNoiseStorage(ManifestStaticFilesStorage):
    """
    WhiteNoise ManifestStaticFilesStorage with three safety overrides:

    1. manifest_strict = False  – prevents runtime KeyError when a hashed
       filename is missing from the manifest (e.g. admin CSS loaded by third-
       party packages that weren't collected).

    2. hashed_name()  – falls back to the original name instead of raising
       ValueError when a file referenced inside CSS/JS cannot be found on disk.
       This is necessary for CKEditor 4 skin files and Jazzmin vendor assets
       that reference texture PNGs not shipped with the package.

    3. post_process()  – wraps the parent generator and skips any file that
       raises FileNotFoundError during processing (e.g. CKEditor highlight
       styles that are referenced in manifests but absent from the package).
    """

    manifest_strict = False

    def hashed_name(self, name, content=None, filename=None):
        try:
            return super().hashed_name(name, content=content, filename=filename)
        except (ValueError, FileNotFoundError):
            # File is referenced in CSS/JS but not present – return as-is
            return name

    def post_process(self, paths, dry_run=False, **options):
        """
        Yield post-processing results, skipping files that cannot be opened.

        WhiteNoise's ManifestStaticFilesStorage tries to open every collected
        file to compute its hash and compress it.  CKEditor ships CSS/JS that
        references sibling files (highlight themes, widget lang packs, etc.)
        which are not always present on disk.  Rather than aborting the entire
        collectstatic run, we catch FileNotFoundError per-file and log a
        warning so the problem is visible without being fatal.
        """
        try:
            for result in super().post_process(paths, dry_run=dry_run, **options):
                # Each result is a (original_path, processed_path, processed) tuple
                # or an exception raised as a yielded value in some Django versions.
                if isinstance(result, Exception):
                    logger.warning(
                        "CustomWhiteNoiseStorage: skipping post-process error: %s", result
                    )
                    continue
                yield result
        except FileNotFoundError as exc:
            logger.warning(
                "CustomWhiteNoiseStorage: FileNotFoundError during post_process, "
                "continuing without full manifest: %s",
                exc,
            )
