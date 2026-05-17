import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env = environ.Env(
    DEBUG=(bool, True),
)

if os.path.exists(os.path.join(BASE_DIR, ".env")):
    environ.Env.read_env(os.path.join(BASE_DIR, ".env"), overwrite=True)

print(f"DEBUG from env: {env.bool('DEBUG', default='NOT FOUND')}")
print(f"ALLOWED_HOSTS from env: {env.list('ALLOWED_HOSTS', default='NOT FOUND')}")
print(f"IS_PRODUCTION from env: {env.bool('IS_PRODUCTION', default='NOT FOUND')}")
