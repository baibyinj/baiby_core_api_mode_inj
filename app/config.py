from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Simple API"
    DATABASE_URL: str = "sqlite:///./test.db"
    TX_AGENT_URL: str = "http://localhost:8001"  # URL del servicio txAgent

settings = Settings() 