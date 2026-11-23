"""Vision LLM client with multi-provider fallback chain."""
import base64
import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict, Any

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .config import get_settings
from .logging import get_logger
from .utils import RateLimiter


class VisionProvider(Enum):
    """Supported vision LLM providers."""
    OPENROUTER = "openrouter"
    OMNIROUTE = "omniroute"
    GEMINI = "gemini"
    OLLAMA = "ollama"


@dataclass
class VisionConfig:
    """Configuration for a vision provider."""
    provider: VisionProvider
    api_key: str
    model: str
    endpoint: str
    timeout: int = 35


class VisionProviderBase(ABC):
    """Abstract base class for vision providers."""

    @abstractmethod
    def call_vision(self, prompt: str, image_bytes: bytes, timeout: int) -> Optional[str]:
        """Call vision model with prompt and image.

        Returns:
            Reply string, empty string if SKIP, None on error
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is configured and available."""
        pass


class OpenRouterVision(VisionProviderBase):
    """OpenRouter vision API provider."""

    def __init__(self, config: VisionConfig):
        self.config = config
        self.logger = get_logger("resrise.vision.openrouter")
        self._rate_limiter = RateLimiter(rate=0.5, burst=2)  # 1 req per 2 sec, burst 2

    def is_available(self) -> bool:
        return bool(self.config.api_key and self.config.model)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((urllib.error.URLError, TimeoutError)),
    )
    def call_vision(self, prompt: str, image_bytes: bytes, timeout: int = 35) -> Optional[str]:
        if not self.is_available():
            return None

        self._rate_limiter.acquire()

        b64_img = base64.b64encode(image_bytes).decode("ascii")
        payload = json.dumps({
            "model": self.config.model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}},
                ],
            }],
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://resrise.studio",
            "X-Title": "Resrise Studio",
        }

        req = urllib.request.Request(self.config.endpoint, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return self._extract_content(data)
        except urllib.error.HTTPError as e:
            self.logger.error("OpenRouter HTTP error", status=e.code, error=e.read().decode())
            raise
        except Exception as e:
            self.logger.error("OpenRouter request failed", error=str(e))
            raise

    def _extract_content(self, data: Dict[str, Any]) -> str:
        choices = data.get("choices") or []
        if not choices:
            return ""
        msg = choices[0].get("message") or {}
        content = msg.get("content")
        if isinstance(content, list):
            parts = [p.get("text", "") for p in content if isinstance(p, dict)]
            content = " ".join(parts)
        reply = (content or "").strip().strip('"')
        return "" if reply.upper().startswith("SKIP") else reply


class OmniRouteVision(VisionProviderBase):
    """OmniRoute (local OpenAI-compatible) vision provider."""

    def __init__(self, config: VisionConfig):
        self.config = config
        self.logger = get_logger("resrise.vision.omniroute")
        self._rate_limiter = RateLimiter(rate=1.0, burst=3)

    def is_available(self) -> bool:
        if not self.config.api_key and not self.config.endpoint:
            return False
        return self._check_health()

    def _check_health(self) -> bool:
        try:
            base = self.config.endpoint.split("/v1/")[0]
            with urllib.request.urlopen(f"{base}/v1/models", timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((urllib.error.URLError, TimeoutError)),
    )
    def call_vision(self, prompt: str, image_bytes: bytes, timeout: int = 30) -> Optional[str]:
        if not self.is_available():
            return None

        self._rate_limiter.acquire()

        b64_img = base64.b64encode(image_bytes).decode("ascii")
        payload = json.dumps({
            "model": self.config.model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}},
                ],
            }],
        }).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        req = urllib.request.Request(self.config.endpoint, data=payload, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["choices"][0]["message"]["content"].strip().strip('"')
                return "" if not reply or reply.upper().startswith("SKIP") else reply
        except Exception as e:
            self.logger.error("OmniRoute request failed", error=str(e))
            raise


class GeminiVision(VisionProviderBase):
    """Google Gemini vision provider."""

    def __init__(self, config: VisionConfig):
        self.config = config
        self.logger = get_logger("resrise.vision.gemini")
        self._rate_limiter = RateLimiter(rate=0.5, burst=1)

    def is_available(self) -> bool:
        return bool(self.config.api_key)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((urllib.error.URLError, TimeoutError)),
    )
    def call_vision(self, prompt: str, image_bytes: bytes, timeout: int = 30) -> Optional[str]:
        if not self.is_available():
            return None

        self._rate_limiter.acquire()

        # 1. Try official google-genai SDK
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.config.api_key)
            contents = [prompt]
            if image_bytes:
                contents.append(types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"))

            model_name = self.config.model or "gemini-3.5-flash"
            if model_name.startswith("models/"):
                model_name = model_name[7:]
            if model_name in ("gemini-2.5-flash", "gemini-2.0-flash"):
                model_name = "gemini-3.5-flash"

            response = client.models.generate_content(
                model=model_name,
                contents=contents,
            )
            reply = (response.text or "").strip().strip('"')
            return "" if not reply or reply.upper().startswith("SKIP") else reply
        except Exception as sdk_err:
            self.logger.warning("google-genai SDK call failed, falling back to REST", error=str(sdk_err))

        # 2. REST Fallback
        b64_img = base64.b64encode(image_bytes).decode("ascii") if image_bytes else ""
        model = self.config.model or "gemini-3.5-flash"
        if model in ("gemini-2.5-flash", "gemini-2.0-flash"):
            model = "gemini-3.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.config.api_key}"
        parts = [{"text": prompt}]
        if b64_img:
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": b64_img}})
        payload = json.dumps({"contents": [{"parts": parts}]}).encode("utf-8")

        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip().strip('"')
                return "" if not reply or reply.upper().startswith("SKIP") else reply
        except Exception as e:
            self.logger.error("Gemini request failed", error=str(e))
            raise


class OllamaVision(VisionProviderBase):
    """Local Ollama vision provider."""

    def __init__(self, config: VisionConfig):
        self.config = config
        self.logger = get_logger("resrise.vision.ollama")
        self._rate_limiter = RateLimiter(rate=0.2, burst=1)  # Slower for local

    def is_available(self) -> bool:
        try:
            base = self.config.endpoint.split("/api/")[0]
            with urllib.request.urlopen(f"{base}/api/tags", timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    @retry(
        wait=wait_exponential(multiplier=1, min=5, max=30),
        stop=stop_after_attempt(2),
        retry=retry_if_exception_type((urllib.error.URLError, TimeoutError)),
    )
    def call_vision(self, prompt: str, image_bytes: bytes, timeout: int = 60) -> Optional[str]:
        if not self.is_available():
            return None

        self._rate_limiter.acquire()

        b64_img = base64.b64encode(image_bytes).decode("ascii")
        payload = json.dumps({
            "model": self.config.model,
            "stream": False,
            "messages": [{"role": "user", "content": prompt, "images": [b64_img]}],
        }).encode("utf-8")

        req = urllib.request.Request(
            self.config.endpoint, data=payload, headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data.get("message", {}).get("content", "").strip().strip('"')
                return "" if not reply or reply.upper().startswith("SKIP") else reply
        except Exception as e:
            self.logger.error("Ollama request failed", error=str(e))
            raise


class VisionClient:
    """Multi-provider vision client with automatic fallback."""

    PROVIDER_ORDER = [
        VisionProvider.OPENROUTER,
        VisionProvider.OMNIROUTE,
        VisionProvider.GEMINI,
        VisionProvider.OLLAMA,
    ]

    def __init__(self):
        self.logger = get_logger("resrise.vision.client")
        self._providers: Dict[VisionProvider, VisionProviderBase] = {}
        self._init_providers()

    def _init_providers(self) -> None:
        """Initialize all providers from settings."""
        settings = get_settings()

        # OpenRouter
        or_key = settings.openrouter_api_key or settings.anthropic_auth_token
        or_endpoint = settings.openrouter_base_url.rstrip("/")
        if not or_endpoint.endswith("/v1"):
            or_endpoint += "/v1"
        or_endpoint += "/chat/completions"

        self._providers[VisionProvider.OPENROUTER] = OpenRouterVision(VisionConfig(
            provider=VisionProvider.OPENROUTER,
            api_key=or_key,
            model=settings.openrouter_model or settings.anthropic_model,
            endpoint=or_endpoint,
        ))

        # OmniRoute
        self._providers[VisionProvider.OMNIROUTE] = OmniRouteVision(VisionConfig(
            provider=VisionProvider.OMNIROUTE,
            api_key=settings.omniroute_api_key,
            model=settings.omniroute_model,
            endpoint=settings.omniroute_url,
        ))

        # Gemini
        self._providers[VisionProvider.GEMINI] = GeminiVision(VisionConfig(
            provider=VisionProvider.GEMINI,
            api_key=settings.gemini_api_key,
            model="gemini-3-flash-preview",
            endpoint="https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
        ))

        # Ollama
        self._providers[VisionProvider.OLLAMA] = OllamaVision(VisionConfig(
            provider=VisionProvider.OLLAMA,
            api_key="",
            model=settings.ollama_model,
            endpoint=settings.ollama_url,
        ))

    def call_vision(self, prompt: str, image_bytes: bytes, timeout: int = 35) -> Optional[str]:
        """
        Call vision model with automatic fallback.

        Returns:
            Reply string, empty string if all providers return SKIP, None if all fail
        """
        last_error = None

        for provider_type in self.PROVIDER_ORDER:
            provider = self._providers[provider_type]
            if not provider.is_available():
                self.logger.debug(f"Provider {provider_type.value} not available, skipping")
                continue

            self.logger.info(f"Trying vision provider: {provider_type.value}")
            try:
                reply = provider.call_vision(prompt, image_bytes, timeout)
                if reply is not None:
                    self.logger.info(f"Vision provider {provider_type.value} succeeded")
                    return reply
                else:
                    self.logger.info(f"Vision provider {provider_type.value} returned SKIP")
            except Exception as e:
                last_error = e
                self.logger.warning(f"Vision provider {provider_type.value} failed", error=str(e))
                continue

        self.logger.error("All vision providers failed", last_error=str(last_error) if last_error else "none available")
        return None

    def is_configured(self) -> bool:
        """Check if at least one provider is available."""
        return any(p.is_available() for p in self._providers.values())

    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [p.value for p in self.PROVIDER_ORDER if self._providers[p].is_available()]


# Text-only client for non-vision tasks
class TextClient:
    """Multi-provider text LLM client with fallback."""

    def __init__(self):
        self.logger = get_logger("resrise.text.client")
        self._vision_client = VisionClient()

    def call_text(self, prompt: str, timeout: int = 30) -> str:
        """Call text model with fallback chain."""
        # Try OpenRouter first
        if self._vision_client._providers[VisionProvider.OPENROUTER].is_available():
            try:
                return self._call_openrouter_text(prompt, timeout)
            except Exception as e:
                self.logger.warning("OpenRouter text failed", error=str(e))

        # Try OmniRoute
        if self._vision_client._providers[VisionProvider.OMNIROUTE].is_available():
            try:
                return self._call_omniroute_text(prompt, timeout)
            except Exception as e:
                self.logger.warning("OmniRoute text failed", error=str(e))

        # Try Gemini
        if self._vision_client._providers[VisionProvider.GEMINI].is_available():
            try:
                return self._call_gemini_text(prompt, timeout)
            except Exception as e:
                self.logger.warning("Gemini text failed", error=str(e))

        return ""

    def _call_openrouter_text(self, prompt: str, timeout: int) -> str:
        settings = get_settings()
        or_key = settings.openrouter_api_key or settings.anthropic_auth_token
        or_endpoint = settings.openrouter_base_url.rstrip("/")
        if not or_endpoint.endswith("/v1"):
            or_endpoint += "/v1"
        or_endpoint += "/chat/completions"

        payload = json.dumps({
            "model": settings.openrouter_model or settings.anthropic_model,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {or_key}",
            "HTTP-Referer": "https://resrise.studio",
            "X-Title": "Resrise Studio",
        }

        req = urllib.request.Request(or_endpoint, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()

    def _call_omniroute_text(self, prompt: str, timeout: int) -> str:
        settings = get_settings()
        payload = json.dumps({
            "model": settings.omniroute_model,
            "messages": [{"role": "user", "content": prompt}],
        }).encode("utf-8")

        headers = {"Content-Type": "application/json"}
        if settings.omniroute_api_key:
            headers["Authorization"] = f"Bearer {settings.omniroute_api_key}"

        req = urllib.request.Request(settings.omniroute_url, data=payload, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()

    def _call_gemini_text(self, prompt: str, timeout: int) -> str:
        settings = get_settings()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={settings.gemini_api_key}"
        payload = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()