from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    REDIS_URL: str = "redis://redis:6379/0"
    DATABASE_URL: str = "mysql+pymysql://user:password@db:3306/task_db"

    class Config:
        env_file = ".env"

settings = Settings()