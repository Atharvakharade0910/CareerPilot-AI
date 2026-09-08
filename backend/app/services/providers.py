"""Provider boundary for Phase 4. Credentials belong only in backend env.
Implementations must validate structured outputs and evidence before persistence.
"""

from typing import Protocol
from pydantic import BaseModel


class StructuredProvider(Protocol):
    async def extract(self, source: str, schema: type[BaseModel]) -> BaseModel: ...


class ProviderUnavailable(RuntimeError):
    pass


def get_provider(name: str) -> StructuredProvider:
    if name not in {"openai", "gemini", "groq"}:
        raise ValueError("Unsupported provider")
    raise ProviderUnavailable(
        "LLM providers are not implemented in Phase 1. Use the local evidence parser."
    )
