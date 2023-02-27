import os

from dynaconf import Dynaconf

APP_DIR = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix=False,
    preload=[os.path.join(APP_DIR, "default.toml")],
    includes=["../configs/*.toml"],
    environments=["local", "development", "docker", "test", "pipeline"],
    env_switcher="identity_server_poc_env",
    load_dotenv=True,
)


DB_URL = settings.db.get("url")
DB_MAX_CONNECTION_COUNT = settings.db.get("max_connection_count")

REDIS_URL = settings.redis.get("url")
