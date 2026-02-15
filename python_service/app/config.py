from enum import StrEnum

from pydantic_settings import BaseSettings


class LLMProvider(StrEnum):
    CLAUDE = "claude"
    OPENAI_COMPAT = "openai"


class Settings(BaseSettings):
    llm_provider: LLMProvider = LLMProvider.CLAUDE
    llm_api_key: str = ""
    llm_model: str = ""
    llm_base_url: str = ""
    minion_host: str = "localhost"
    minion_port: int = 19800
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_prefix": "NLP_BRIDGE_"}

    @property
    def resolved_model(self) -> str:
        if self.llm_model:
            return self.llm_model
        if self.llm_provider == LLMProvider.CLAUDE:
            return "claude-sonnet-4-5-20250929"
        return "default"

    @property
    def resolved_base_url(self) -> str:
        if self.llm_base_url:
            return self.llm_base_url
        if self.llm_provider == LLMProvider.OPENAI_COMPAT:
            return "http://localhost:8080/v1"
        return ""

    @property
    def minion_url(self) -> str:
        return f"http://{self.minion_host}:{self.minion_port}"


settings = Settings()
