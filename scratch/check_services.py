import os
import environ
import psycopg2
import redis
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
env = environ.Env()
if os.path.exists(os.path.join(BASE_DIR, ".env")):
    environ.Env.read_env(os.path.join(BASE_DIR, ".env"), overwrite=True)
    print("Loaded environment variables from .env")
else:
    print(".env file not found!")

# 1. Test database connection
db_url = os.environ.get("DATABASE_URL")
if db_url:
    print(f"\n[Database] Attempting connection to: {db_url.split('@')[-1]}")
    try:
        conn = psycopg2.connect(db_url, connect_timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        print(f"[Database] SUCCESS! Connection established. Version: {db_version[0]}")
        
        cursor.execute("SELECT COUNT(*) FROM pg_stat_activity;")
        connections = cursor.fetchone()[0]
        print(f"[Database] Current active connections: {connections}")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[Database] FAILURE: {e}")
else:
    print("\n[Database] DATABASE_URL not set in env.")

# 2. Test Redis connection
redis_url = os.environ.get("REDIS_URL")
if redis_url:
    print(f"\n[Redis] Attempting connection to Redis instance...")
    try:
        r = redis.from_url(redis_url, socket_connect_timeout=5)
        ping_res = r.ping()
        print(f"[Redis] SUCCESS! Ping response: {ping_res}")
    except Exception as e:
        print(f"[Redis] FAILURE: {e}")
else:
    print("\n[Redis] REDIS_URL not set in env.")
