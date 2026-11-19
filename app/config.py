from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    db_url: str
    signature_key: str
    algorithm:str
    token_expiry_time: int
    initial_admin_password: str
    
    model_config = SettingsConfigDict(
        env_file = ".env" if Path(".env").exists else Path(".env.example"),
        env_parse_json = True
    )
    
settings = Settings()