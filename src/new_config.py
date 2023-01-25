import os

from dynaconf import Dynaconf

APP_DIR = os.path.dirname(os.path.abspath(__file__))

settings = Dynaconf(
    envvar_prefix="cinema",
    preload=[os.path.join(APP_DIR, "default.toml")],
    includes=["../configs/*.toml"],
    environments=["local", "development", "docker"],
    env_switcher="identity_server_poc_env",
    load_dotenv=True,
)


DB_URI = settings.db.get("uri")


REDIS_URL = settings.redis.get("host")
REDIS_PORT = settings.redis.get("port")
REDIS_CACHE_DB = settings.redis.get("cache_db")
REDIS_USER = settings.redis.get("user")
REDIS_PASSWORD = settings.redis.get("password")


IS_LOCAL = settings.env_for_dynaconf == "local"
IS_DEVELOPMENT = settings.env_for_dynaconf == "development"
IS_DOCKER = settings.env_for_dynaconf == "docker"
IS_PRODUCTION = settings.env_for_dynaconf == "production"

data = settings.as_dict(env="development")
