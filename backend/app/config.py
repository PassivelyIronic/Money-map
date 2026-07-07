from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Postgres
    database_url: str = "postgresql://money_map:money_map@postgres:5432/money_map"

    # Redis / Celery
    redis_url: str = "redis://redis:6379/0"

    # Ollama, wolan na hoście (Windows/WSL), nie w docker-compose
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "qwen2.5:7b-instruct"

    # OpenRouter, fallback do miesiecznych insightow, zero-cost tier
    openrouter_api_key: str | None = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    # Lista darmowych modeli zmienia sie co kilka tygodni, sprawdz aktualna
    # na openrouter.ai/models z filtrem :free zanim odpalisz w produkcji
    openrouter_model: str = "meta-llama/llama-3.3-70b-instruct:free"

    # App
    debug: bool = True


settings = Settings()
