from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./payments.db"
    secret_key: str = "dev-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Límites por nivel de verificación
    limits_basic: dict = {
        "max_cards": 2,
        "max_transaction": 500.0,
        "daily_limit": 1000.0,
        "monthly_limit": 5000.0
    }
    limits_verified: dict = {
        "max_cards": 5,
        "max_transaction": 5000.0,
        "daily_limit": 10000.0,
        "monthly_limit": 50000.0
    }
    limits_premium: dict = {
        "max_cards": 10,
        "max_transaction": 50000.0,
        "daily_limit": 100000.0,
        "monthly_limit": 500000.0
    }

    class Config:
        env_file = ".env"


settings = Settings()