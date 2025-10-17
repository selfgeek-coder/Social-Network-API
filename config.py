from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KEY: str
    ALGORITHM: str
    
    class Config:
        env_file = ".env"

settings = Settings()

secret_key = settings.KEY
algorithm = settings.ALGORITHM