"""Tests for configuration management."""
import os
import tempfile
from pathlib import Path

import pytest

from scripts.core.config import Settings, load_settings, get_settings, load_config


class TestSettings:
    """Test Settings class."""

    def test_default_values(self):
        """Test default configuration values."""
        settings = Settings()
        assert settings.openrouter_model == "inclusionai/ling-3.2-flash:free"
        assert settings.anthropic_model == "inclusionai/ling-3.2-flash:free"
        assert settings.omniroute_model == "gemini/gemini-3-flash-preview"
        assert settings.ollama_model == "gemma3:4b"
        assert settings.instagram_accounts == (
            "avanyamehra",
            "mairamehraofficial",
            "iamgagankumar",
            "resrise",
            "gagankumarrocks",
        )

    def test_env_override(self, monkeypatch):
        """Test environment variable overrides."""
        monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-123")
        monkeypatch.setenv("OPENROUTER_MODEL", "custom/model")
        monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")

        settings = Settings()
        assert settings.openrouter_api_key == "test-key-123"
        assert settings.openrouter_model == "custom/model"
        assert settings.gemini_api_key == "gemini-key"

    def test_project_dir_property(self):
        """Test project_dir property resolves correctly."""
        settings = Settings()
        assert settings.project_dir.name == "resrise-studio"
        assert (settings.project_dir / "scripts").exists()

    def test_draft_media_dir_property(self):
        """Test draft_media_dir property."""
        settings = Settings()
        assert settings.draft_media_dir == settings.project_dir / "draft_media"

    def test_queue_path_property(self):
        """Test queue_path property."""
        settings = Settings()
        assert settings.queue_path == settings.project_dir / "swarm_queue.json"

    def test_accounts_config_path_property(self):
        """Test accounts_config_path property."""
        settings = Settings()
        assert settings.accounts_config_path == settings.project_dir / "scripts" / "accounts_config.json"

    def test_get_chrome_profile_dir(self):
        """Test Chrome profile directory generation."""
        settings = Settings()
        profile_dir = settings.get_chrome_profile_dir("avanyamehra")
        assert "avanyamehra" in str(profile_dir)
        assert "User Data - Automation" in str(profile_dir)


class TestLoadSettings:
    """Test settings loading functions."""

    def test_load_settings_singleton(self):
        """Test that load_settings returns singleton."""
        s1 = load_settings()
        s2 = load_settings()
        assert s1 is s2

    def test_get_settings_loads_if_needed(self):
        """Test get_settings loads if not already loaded."""
        # Reset global
        import scripts.core.config as config_module
        config_module._settings = None

        s = get_settings()
        assert isinstance(s, Settings)


class TestLoadConfig:
    """Test accounts config loading."""

    def test_load_config_existing(self, tmp_path, monkeypatch):
        """Test loading existing config file."""
        config_file = tmp_path / "accounts_config.json"
        config_file.write_text('{"accounts": {"test": {"name": "Test"}}}')

        # Monkey patch get_settings to return mock settings
        import scripts.core.config as config_module

        class MockSettings:
            accounts_config_path = config_file

        monkeypatch.setattr(config_module, "_settings", MockSettings())

        result = load_config()
        assert result == {"accounts": {"test": {"name": "Test"}}}

    def test_load_config_missing(self, tmp_path, monkeypatch):
        """Test loading missing config file returns empty."""
        missing_file = tmp_path / "missing.json"

        import scripts.core.config as config_module

        class MockSettings:
            accounts_config_path = missing_file

        monkeypatch.setattr(config_module, "_settings", MockSettings())

        result = load_config()
        assert result == {"accounts": {}}