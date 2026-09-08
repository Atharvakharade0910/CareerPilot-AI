from pydantic import BaseModel
from app.core.config import settings

class GeminiUnavailable(RuntimeError): pass

async def generate(prompt: str, schema: type[BaseModel] | None = None):
    if not settings.gemini_api_key: raise GeminiUnavailable("Gemini is not configured")
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())
        cfg = types.GenerateContentConfig(response_mime_type="application/json" if schema else "text/plain", response_schema=schema.model_json_schema() if schema else None, system_instruction="You are an evidence-grounded career coach. Never invent candidate experience or metrics.")
        result = client.models.generate_content(model=settings.gemini_model, contents=prompt, config=cfg)
        return schema.model_validate_json(result.text).model_dump() if schema else result.text
    except Exception as exc:
        raise GeminiUnavailable(f"Gemini request failed: {type(exc).__name__}") from exc
