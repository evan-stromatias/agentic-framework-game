"""
Each provider has its own env variable for the API_KEY:
    - https://docs.litellm.ai/docs/providers
"""

from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    LLM_MODEL: Optional[str] = None
    LLM_API_KEY: Optional[str] = None
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: Optional[int] = None
    LLM_BASE_URL: Optional[str] = None
    LITE_LLM_MAX_RETRIES: int = 3
    AGENT_SLEEP_SECS: Optional[int] = None

    LOG_LEVEL: str = "DEBUG"
    LOG_FILE: Optional[str] = None


def get_settings() -> Settings:
    return Settings()
