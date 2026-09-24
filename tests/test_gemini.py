import asyncio
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from google import genai
from pydantic import BaseModel, SecretStr

from app.services import gemini


class Answer(BaseModel):
    answer: str


@pytest.mark.parametrize("mode", ["text", "structured", "provider_error", "invalid_json"])
def test_client_cleanup_on_success_and_failure(monkeypatch, mode):
    client = MagicMock(spec=genai.Client)
    client.__enter__.return_value = client
    client.__exit__.side_effect = lambda *args: client.close() and False
    client.models = MagicMock()
    client.models.generate_content.return_value = SimpleNamespace(
        text='{"answer":"Example"}' if mode == "structured" else "Example"
    )
    if mode == "provider_error":
        client.models.generate_content.side_effect = RuntimeError("Synthetic failure")
    monkeypatch.setattr(genai, "Client", lambda **kwargs: client)
    monkeypatch.setattr(gemini.settings, "gemini_api_key", SecretStr("test-only-placeholder"))
    schema = Answer if mode in {"structured", "invalid_json"} else None

    if mode in {"provider_error", "invalid_json"}:
        with pytest.raises(gemini.GeminiUnavailable):
            asyncio.run(gemini.generate("Example question", schema))
    else:
        result = asyncio.run(gemini.generate("Example question", schema))
        assert result == ({"answer": "Example"} if schema else "Example")
    client.close.assert_called_once()
