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
# DB_PORT = settings.db.get("port")


BASE_URL_HOST = settings.server.get("base_url_host")
BASE_URL_PORT = settings.server.get("base_url_port")
BASE_URL = f"{BASE_URL_HOST}:{BASE_URL_PORT}"
DOMAIN_NAME = settings.server.get("domain_name")

REDIS_SCHEME = settings.redis.get("scheme")
REDIS_HOST = settings.redis.get("host")
REDIS_PORT = settings.redis.get("port")
REDIS_URL = f"{REDIS_SCHEME}{REDIS_HOST}:{REDIS_PORT}"


# IS_CLIENT = settings.env_for_dynaconf not in (
#     "local",
#     "development",
#     "docker",
#     "test",
#     "pipeline",
# )
#
# if not IS_CLIENT:
#     DB_URL = settings.db.get("url")
# else:
#     DB_USER = settings.DB_USER
#     DB_PASSWORD = settings.DB_PASSWORD
#     DB_HOST = settings.DB_HOST
#     DB_PORT = settings.DB_PORT
#     DB_NAME = settings.DB_NAME
#     DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
