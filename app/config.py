from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Simple API"
    DATABASE_URL: str = "sqlite:///./test.db"

settings = Settings() 