"""Tests for vision client and providers."""
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import pytest

from scripts.core.vision import (
    VisionProvider,
    VisionConfig,
    OpenRouterVision,
    OmniRouteVision,
    GeminiVision,
    OllamaVision,
    VisionClient,
    TextClient,
)


class TestVisionConfig:
    """Test VisionConfig dataclass."""

    def test_vision_config_creation(self):
        """Test VisionConfig creation."""
        config = VisionConfig(
            provider=VisionProvider.OPENROUTER,
            api_key="test-key",
            model="test-model",
            endpoint="https://api.test.com",
            timeout=30,
        )
        assert config.provider == VisionProvider.OPENROUTER
        assert config.api_key == "test-key"
        assert config.model == "test-model"
        assert config.endpoint == "https://api.test.com"
        assert config.timeout == 30


class TestOpenRouterVision:
    """Test OpenRouter vision provider."""

    @pytest.fixture
    def config(self):
        return VisionConfig(
            provider=VisionProvider.OPENROUTER,
            api_key="test-key",
            model="test-model",
            endpoint="https://api.test.com/v1/chat/completions",
        )

    def test_is_available_with_key(self, config):
        """Test is_available returns True with API key."""
        provider = OpenRouterVision(config)
        assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test is_available returns False without API key."""
        config = VisionConfig(
            provider=VisionProvider.OPENROUTER,
            api_key="",
            model="test-model",
            endpoint="https://api.test.com",
        )
        provider = OpenRouterVision(config)
        assert provider.is_available() is False

    @patch("scripts.core.vision.urllib.request.urlopen")
    def test_call_vision_success(self, mock_urlopen, config):
        """Test successful vision call."""
        provider = OpenRouterVision(config)

        # Mock response
        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "A beautiful sunset photo"
                }
            }]
        }).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = provider.call_vision("Describe this image", b"fake-image-data")

        assert result == "A beautiful sunset photo"
        mock_urlopen.assert_called_once()

    @patch("scripts.core.vision.urllib.request.urlopen")
    def test_call_vision_skip_response(self, mock_urlopen, config):
        """Test SKIP response handling."""
        provider = OpenRouterVision(config)

        mock_response = Mock()
        mock_response.read.return_value = json.dumps({
            "choices": [{
                "message": {
                    "content": "SKIP"
                }
            }]
        }).encode()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = provider.call_vision("Describe this image", b"fake-image-data")

        assert result == ""

    @patch("scripts.core.vision.urllib.request.urlopen")
    def test_call_vision_http_error(self, mock_urlopen, config):
        """Test HTTP error handling."""
        import urllib.error

        provider = OpenRouterVision(config)

        mock_response = Mock()
        mock_response.read.return_value = b'{"error": "rate limit"}'
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        http_error = urllib.error.HTTPError(
            "https://api.test.com", 429, "Too Many Requests", {}, mock_response
        )
        mock_urlopen.side_effect = http_error

        # Retry decorator will retry 3 times then raise RetryError
        with pytest.raises(Exception):
            provider.call_vision("Describe this image", b"fake-image-data")


class TestOmniRouteVision:
    """Test OmniRoute vision provider."""

    @pytest.fixture
    def config(self):
        return VisionConfig(
            provider=VisionProvider.OMNIROUTE,
            api_key="omni-key",
            model="gemini/gemini-3-flash-preview",
            endpoint="http://localhost:20128/v1/chat/completions",
        )

    @patch("scripts.core.vision.urllib.request.urlopen")
    def test_is_available_healthy(self, mock_urlopen, config):
        """Test is_available when OmniRoute is healthy."""
        provider = OmniRouteVision(config)

        # Mock health check
        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        assert provider.is_available() is True

    @patch("scripts.core.vision.urllib.request.urlopen")
    def test_is_available_unhealthy(self, mock_urlopen, config):
        """Test is_available when OmniRoute is unhealthy."""
        provider = OmniRouteVision(config)
        mock_urlopen.side_effect = Exception("Connection refused")

        assert provider.is_available() is False


class TestGeminiVision:
    """Test Gemini vision provider."""

    @pytest.fixture
    def config(self):
        return VisionConfig(
            provider=VisionProvider.GEMINI,
            api_key="gemini-key",
            model="gemini-3-flash-preview",
            endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
        )

    def test_is_available_with_key(self, config):
        """Test is_available with API key."""
        provider = GeminiVision(config)
        assert provider.is_available() is True

    def test_is_available_without_key(self):
        """Test is_available without API key."""
        config = VisionConfig(
            provider=VisionProvider.GEMINI,
            api_key="",
            model="gemini-3-flash-preview",
            endpoint="https://api.test.com",
        )
        provider = GeminiVision(config)
        assert provider.is_available() is False


class TestOllamaVision:
    """Test Ollama vision provider."""

    @pytest.fixture
    def config(self):
        return VisionConfig(
            provider=VisionProvider.OLLAMA,
            api_key="",
            model="gemma3:4b",
            endpoint="http://localhost:11434/api/chat",
        )

    @patch("scripts.core.vision.urllib.request.urlopen")
    def test_is_available_healthy(self, mock_urlopen, config):
        """Test is_available when Ollama is healthy."""
        provider = OllamaVision(config)

        mock_response = Mock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response

        assert provider.is_available() is True


class TestVisionClient:
    """Test multi-provider vision client."""

    def test_init(self):
        """Test VisionClient initialization."""
        client = VisionClient()
        assert hasattr(client, "_providers")
        assert len(client._providers) == 4

    @patch("scripts.core.vision.VisionClient._init_providers")
    def test_call_vision_fallback_chain(self, mock_init):
        """Test fallback chain when providers fail."""
        client = VisionClient()

        # Mock providers - first fails, second succeeds
        mock_provider1 = Mock()
        mock_provider1.is_available.return_value = True
        mock_provider1.call_vision.side_effect = Exception("Failed")

        mock_provider2 = Mock()
        mock_provider2.is_available.return_value = True
        mock_provider2.call_vision.return_value = "Success from provider 2"

        client._providers = {
            VisionProvider.OPENROUTER: mock_provider1,
            VisionProvider.OMNIROUTE: mock_provider2,
            VisionProvider.GEMINI: Mock(is_available=Mock(return_value=False)),
            VisionProvider.OLLAMA: Mock(is_available=Mock(return_value=False)),
        }

        result = client.call_vision("Test prompt", b"image-data")

        assert result == "Success from provider 2"
        mock_provider1.call_vision.assert_called_once()
        mock_provider2.call_vision.assert_called_once()

    @patch("scripts.core.vision.VisionClient._init_providers")
    def test_call_vision_all_fail(self, mock_init):
        """Test when all providers fail."""
        client = VisionClient()

        mock_provider = Mock()
        mock_provider.is_available.return_value = True
        mock_provider.call_vision.side_effect = Exception("All failed")

        client._providers = {
            VisionProvider.OPENROUTER: mock_provider,
            VisionProvider.OMNIROUTE: Mock(is_available=Mock(return_value=False)),
            VisionProvider.GEMINI: Mock(is_available=Mock(return_value=False)),
            VisionProvider.OLLAMA: Mock(is_available=Mock(return_value=False)),
        }

        result = client.call_vision("Test prompt", b"image-data")

        assert result is None

    @patch("scripts.core.vision.VisionClient._init_providers")
    def test_is_configured(self, mock_init):
        """Test is_configured method."""
        client = VisionClient()

        client._providers = {
            VisionProvider.OPENROUTER: Mock(is_available=Mock(return_value=True)),
            VisionProvider.OMNIROUTE: Mock(is_available=Mock(return_value=False)),
            VisionProvider.GEMINI: Mock(is_available=Mock(return_value=False)),
            VisionProvider.OLLAMA: Mock(is_available=Mock(return_value=False)),
        }

        assert client.is_configured() is True

    @patch("scripts.core.vision.VisionClient._init_providers")
    def test_get_available_providers(self, mock_init):
        """Test get_available_providers method."""
        client = VisionClient()

        client._providers = {
            VisionProvider.OPENROUTER: Mock(is_available=Mock(return_value=True)),
            VisionProvider.OMNIROUTE: Mock(is_available=Mock(return_value=True)),
            VisionProvider.GEMINI: Mock(is_available=Mock(return_value=False)),
            VisionProvider.OLLAMA: Mock(is_available=Mock(return_value=True)),
        }

        available = client.get_available_providers()
        assert set(available) == {"openrouter", "omniroute", "ollama"}


class TestTextClient:
    """Test text-only client."""

    @patch("scripts.core.vision.VisionClient")
    def test_call_text_fallback(self, mock_vision_client_class):
        """Test text client fallback chain."""
        mock_vision_client = Mock()
        mock_vision_client_class.return_value = mock_vision_client

        # Mock OpenRouter provider
        mock_or_provider = Mock()
        mock_or_provider.is_available.return_value = True
        mock_vision_client._providers = {
            VisionProvider.OPENROUTER: mock_or_provider,
            VisionProvider.OMNIROUTE: Mock(is_available=Mock(return_value=False)),
            VisionProvider.GEMINI: Mock(is_available=Mock(return_value=False)),
            VisionProvider.OLLAMA: Mock(is_available=Mock(return_value=False)),
        }

        # Mock the internal _call_openrouter_text
        with patch.object(TextClient, "_call_openrouter_text", return_value="OpenRouter response") as mock_call:
            client = TextClient()
            result = client.call_text("Test prompt")

            assert result == "OpenRouter response"
            mock_call.assert_called_once()