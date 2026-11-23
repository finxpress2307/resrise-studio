import base64
import json
import os
import urllib.error
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "inclusionai/ling-3.2-flash:free"


def _load_setting_env() -> dict:
    for filename in ("setting.json", "settings.json"):
        path = os.path.join(PROJECT_DIR, filename)
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                env_block = data.get("env") if isinstance(data, dict) else None
                if isinstance(env_block, dict):
                    return env_block
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
    return {}


def get_openrouter_config() -> dict:
    file_env = _load_setting_env()

    api_key = (
        os.environ.get("OPENROUTER_API_KEY")
        or file_env.get("OPENROUTER_API_KEY")
        or file_env.get("ANTHROPIC_AUTH_TOKEN")
        or ""
    ).strip()

    model = (
        os.environ.get("OPENROUTER_MODEL")
        or file_env.get("OPENROUTER_MODEL")
        or file_env.get("ANTHROPIC_MODEL")
        or DEFAULT_MODEL
    ).strip()

    base_url = (
        os.environ.get("OPENROUTER_BASE_URL")
        or file_env.get("OPENROUTER_BASE_URL")
        or file_env.get("ANTHROPIC_BASE_URL")
        or DEFAULT_BASE_URL
    ).strip().rstrip("/")

    if not base_url.endswith("/chat/completions"):
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"
        endpoint = f"{base_url}/chat/completions"
    else:
        endpoint = base_url

    return {
        "api_key": api_key,
        "model": model,
        "endpoint": endpoint,
    }


def is_openrouter_configured() -> bool:
    cfg = get_openrouter_config()
    return bool(cfg["api_key"] and cfg["model"])


def _extract_content(data: dict) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if isinstance(content, list):
        parts = [p.get("text", "") for p in content if isinstance(p, dict)]
        content = " ".join(parts)
    return (content or "").strip()


def call_openrouter_text(prompt: str, timeout: int = 35) -> str:
    cfg = get_openrouter_config()
    if not cfg["api_key"]:
        return ""

    payload = json.dumps({
        "model": cfg["model"],
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {cfg['api_key']}",
        "HTTP-Referer": "https://resrise.studio",
        "X-Title": "Resrise Studio",
    }
    req = urllib.request.Request(cfg["endpoint"], data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return _extract_content(data)
    except Exception:
        return ""


def call_openrouter_vision(prompt: str, image_bytes: bytes, timeout: int = 45):
    """Returns reply string, '' if model responded SKIP, or None on API/network error."""
    cfg = get_openrouter_config()
    if not cfg["api_key"]:
        return None

    b64_img = base64.b64encode(image_bytes).decode("ascii")
    payload = json.dumps({
        "model": cfg["model"],
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
        "Authorization": f"Bearer {cfg['api_key']}",
        "HTTP-Referer": "https://resrise.studio",
        "X-Title": "Resrise Studio",
    }
    req = urllib.request.Request(cfg["endpoint"], data=payload, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            reply = _extract_content(data).strip('"')
            if not reply:
                return None
            return "" if reply.upper().startswith("SKIP") else reply
    except Exception:
        return None
