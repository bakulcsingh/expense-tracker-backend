import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    # API settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Expense Tracker API"
    
    # PostgreSQL database settings
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "TweetyBaba351")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "expense_tracker")
    SQLALCHEMY_DATABASE_URI: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    # JWT token settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "5328a35fd70364f45e9023ff3ee607190879134850f874d982bed735d727fa88")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 24 * 60  # 30 days
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",  # Next.js frontend
        "http://localhost:8000",  # API local development
    ]
    
    class Config:
        env_file = ".env"

settings = Settings()