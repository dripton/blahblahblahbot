# Configure BBBB from the environment if the config hasn't been otherwise provided
import os


class NoConfiguration(Exception):
    ...


def read_config(env_var: str) -> str:
    try:
        return os.environ[env_var]
    except KeyError:
        raise NoConfiguration(f"Unable to read the configuration from {env_var}")


nickname = read_config("BBBB_NICKNAME")
serverhost = read_config("BBBB_IRC_SERVER")
serverport = int(read_config("BBBB_IRC_PORT"))
channels = [_.strip() for _ in read_config("BBBB_IRC_CHANNELS").split(",")]
admins = [_.strip() for _ in read_config("BBBB_ADMIN_NICKNAMES").split(",")]
sqlite_path = read_config("BBBB_SQLITE_DB_URL")
