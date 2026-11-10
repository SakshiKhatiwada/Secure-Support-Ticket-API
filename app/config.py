from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    signature_key: str
    token_expiry_time: int
    
    model_config = SettingsConfigDict(
        env_file = ".env" if Path(".env").exists else Path(".env.example"),
        env_parse_json = True
    )
    
settings = Settings()