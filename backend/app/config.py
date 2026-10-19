import os


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


class Settings:
    SECRET_KEY: str = _require_env("SECRET_KEY")
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test_platform.db")
    ADMIN_USERNAME: str = _require_env("ADMIN_USERNAME")
    ADMIN_PASSWORD: str = _require_env("ADMIN_PASSWORD")
    EXECUTE_TIMEOUT: float = float(os.getenv("EXECUTE_TIMEOUT", "10"))


settings = Settings()
