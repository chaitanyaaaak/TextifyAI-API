from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "TextifyAI API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "production"

    # LLM (OpenRouter/OpenAI compatible)
    OPENROUTER_API_KEY: str = Field(..., env="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_MODEL: str = Field("google/gemini-2.0-flash-001", env="LLM_MODEL")

    # CORS
    # In production, set this to your actual frontend URL (e.g., https://textify.onrender.com)
    FRONTEND_URL: str = Field("https://textify-ai-seven.vercel.app", env="FRONTEND_URL")

    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=True
    )


settings = Settings()
