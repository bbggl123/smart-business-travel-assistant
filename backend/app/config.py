from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    debug: bool = True
    log_level: str = "INFO"

    zidongtaichu_api_key: str
    zidongtaichu_api_url: str = "https://cloud.zidongtaichu.com/maas/v1/chat/completions"
    zidongtaichu_model: str = "Kimi-K2.5"

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_password: str

    redis_host: str
    redis_port: int = 6379
    redis_password: str

    amap_api_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
