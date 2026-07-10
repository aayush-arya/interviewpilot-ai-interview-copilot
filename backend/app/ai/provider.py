"""AI provider abstraction (DIP seam).

Services depend on AIProvider only. ClaudeProvider talks to the Anthropic API;
MockAIProvider produces deterministic, schema-valid output so the entire app
runs (and is tested in CI) without an API key.
"""
import logging
import time
from abc import ABC, abstractmethod

from pydantic import BaseModel, ValidationError

from app.ai.json_utils import extract_json
from app.core.config import get_settings

logger = logging.getLogger("ai")


class AIProvider(ABC):
    @abstractmethod
    def complete(
        self,
        *,
        system: str,
        messages: list[dict],
        chain: str,
        max_tokens: int = 800,
        json_mode: bool = False,
        deep: bool = False,
    ) -> str:
        """Return raw model text. `chain` labels the call for logging/mocking."""


class ClaudeProvider(AIProvider):
    def __init__(self, api_key: str):
        import anthropic

        self._client = anthropic.Anthropic(api_key=api_key)

    def complete(self, *, system, messages, chain, max_tokens=800, json_mode=False, deep=False):
        settings = get_settings()
        model = settings.AI_MODEL_DEEP if deep else settings.AI_MODEL
        request_messages = list(messages)
        if json_mode:
            # Prefill steers the model straight into the object.
            request_messages = request_messages + [{"role": "assistant", "content": "{"}]
        start = time.monotonic()
        response = self._client.messages.create(
            model=model,
            system=system,
            messages=request_messages,
            max_tokens=max_tokens,
        )
        text = response.content[0].text
        if json_mode:
            text = "{" + text
        logger.info(
            "chain=%s model=%s latency_ms=%d in_tokens=%d out_tokens=%d",
            chain, model, (time.monotonic() - start) * 1000,
            response.usage.input_tokens, response.usage.output_tokens,
        )
        return text


def call_structured(
    provider: AIProvider,
    model_cls: type[BaseModel],
    *,
    system: str,
    messages: list[dict],
    chain: str,
    max_tokens: int = 800,
    deep: bool = False,
) -> BaseModel:
    """JSON-mode call parsed+validated against `model_cls`, one retry on failure."""
    last_error: Exception | None = None
    for attempt in range(2):
        msgs = messages
        if attempt == 1:
            msgs = messages + [
                {
                    "role": "user",
                    "content": f"Your previous response was invalid ({last_error}). "
                    "Respond again with ONLY the JSON object, exactly matching the schema.",
                }
            ]
        raw = provider.complete(
            system=system, messages=msgs, chain=chain,
            max_tokens=max_tokens, json_mode=True, deep=deep,
        )
        try:
            return model_cls.model_validate(extract_json(raw))
        except (ValueError, ValidationError) as e:
            last_error = e
            logger.warning("chain=%s attempt=%d parse failure: %s", chain, attempt, e)
    raise RuntimeError(f"AI chain '{chain}' returned unparseable output: {last_error}")


_provider_singleton: AIProvider | None = None


def get_ai_provider() -> AIProvider:
    """FastAPI dependency. Overridden in tests."""
    global _provider_singleton
    if _provider_singleton is None:
        key = get_settings().ANTHROPIC_API_KEY
        if key:
            _provider_singleton = ClaudeProvider(key)
            logger.info("AI provider: Claude (%s)", get_settings().AI_MODEL)
        else:
            from app.ai.mock_provider import MockAIProvider

            _provider_singleton = MockAIProvider()
            logger.warning("ANTHROPIC_API_KEY not set — using MockAIProvider (offline demo mode)")
    return _provider_singleton
