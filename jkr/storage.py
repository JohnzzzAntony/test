from whitenoise.storage import CompressedManifestStaticFilesStorage

class CustomWhiteNoiseStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False

    def post_process(self, *args, **kwargs):
        for name, hashed_name, processed in super().post_process(*args, **kwargs):
            if isinstance(processed, Exception):
                print(f"WARNING: Suppressing MissingFileError during collectstatic for {name}")
                # Yield a successful result to prevent collectstatic from crashing
                yield name, hashed_name, True
            else:
                yield name, hashed_name, processed

