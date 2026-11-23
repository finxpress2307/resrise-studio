"""Configuration management for Resrise Studio automation scripts."""
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenRouter (Primary)
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")
    openrouter_model: str = Field(
        default="inclusionai/ling-3.2-flash:free", alias="OPENROUTER_MODEL"
    )
    openrouter_base_url: str = Field(
        default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL"
    )

    # Anthropic-compatible (OpenRouter proxy)
    anthropic_auth_token: str = Field(default="", alias="ANTHROPIC_AUTH_TOKEN")
    anthropic_model: str = Field(
        default="inclusionai/ling-3.2-flash:free", alias="ANTHROPIC_MODEL"
    )
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    anthropic_base_url: str = Field(
        default="https://openrouter.ai/api/v1", alias="ANTHROPIC_BASE_URL"
    )

    # Local fallbacks
    omniroute_url: str = Field(
        default="http://localhost:20128/v1/chat/completions", alias="OMNIROUTE_URL"
    )
    omniroute_model: str = Field(
        default="gemini/gemini-3-flash-preview", alias="OMNIROUTE_MODEL"
    )
    omniroute_api_key: str = Field(default="", alias="OMNIROUTE_API_KEY")

    gemini_api_key: str = Field(default="", alias="GEMINI_API_KEY")

    ollama_url: str = Field(
        default="http://localhost:11434/api/chat", alias="OLLAMA_URL"
    )
    ollama_model: str = Field(default="gemma3:4b", alias="OLLAMA_MODEL")

    # Instagram
    instagram_accounts: tuple[str, ...] = (
        "avanyamehra",
        "mairamehraofficial",
        "iamgagankumar",
        "resrise",
        "gagankumarrocks",
    )

    # Paths
    @property
    def project_dir(self) -> Path:
        return Path(__file__).resolve().parents[2]

    @property
    def scripts_dir(self) -> Path:
        return self.project_dir / "scripts"

    @property
    def draft_media_dir(self) -> Path:
        return self.project_dir / "draft_media"

    @property
    def queue_path(self) -> Path:
        return self.project_dir / "swarm_queue.json"

    @property
    def accounts_config_path(self) -> Path:
        return self.scripts_dir / "accounts_config.json"

    def get_chrome_profile_dir(self, account: str) -> Path:
        """Get Chrome user data directory for an account."""
        import os
        local_app_data = os.environ.get(
            "LOCALAPPDATA", r"C:\Users\Default\AppData\Local"
        )
        return Path(local_app_data) / "Google" / "Chrome" / "User Data - Automation" / account


_settings: Optional[Settings] = None


def load_settings() -> Settings:
    """Load and cache settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_settings() -> Settings:
    """Get cached settings (load if needed)."""
    if _settings is None:
        return load_settings()
    return _settings


def load_config() -> dict:
    """Load accounts configuration from JSON file."""
    import json
    settings = get_settings()
    path = settings.accounts_config_path
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"accounts": {}}