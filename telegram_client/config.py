import os

from dotenv import load_dotenv


class ConfigManager:
    """This is a config manager that will read everything from .env file
    then you can access it using config.get(key)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        load_dotenv(dotenv_path=env_path)
        self._config = {key: value for key, value in os.environ.items()}

    def get(self, key: str, default=None) -> str:
        return self._config.get(key, default)


# export singleton config object
config = ConfigManager()
