from utility.BaseSettings import BaseSettings
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class DiscordSettings(BaseSettings):
    DISCORD_WEBHOOK_URL: str | None = None

@dataclass
class WebSettings(BaseSettings):
    PORT: int | None = None
    WHITELIST: list[str] | None = None
    USE_WHITELIST: bool | None = None
    PASSWORD: str | None = None

@dataclass
class ExchangeSettings(BaseSettings):
    MASTER_APP_KEY: str | None = None
    MASTER_SECRET_KEY : str | None = None
    SLAVE1_APP_KEY : str | None = None
    SLAVE1_SECRET_KEY : str | None = None
    SLAVE2_APP_KEY : str | None = None
    SLAVE2_SECRET_KEY : str | None = None

@dataclass
class TotalSettings(ExchangeSettings, DiscordSettings, WebSettings):
    pass

@lru_cache()
def get_settings():
    return TotalSettings()

# global instance
settings = get_settings()


# test
if __name__ == "__main__":
    print(settings)