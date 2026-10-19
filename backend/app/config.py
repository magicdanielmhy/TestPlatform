import os


class Settings:
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "dev-secret-key-change-me-0123456789abcdef"
    )
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test_platform.db")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    EXECUTE_TIMEOUT: float = float(os.getenv("EXECUTE_TIMEOUT", "10"))


settings = Settings()
