from functools import lru_cache

from app.config import settings
from app.llm.base import LLMClient
from app.llm.bedrock_client import BedrockClient
from app.llm.openai_client import OpenAIClient


@lru_cache
def get_llm_client() -> LLMClient:
    """settings.llm_provider に応じてBedrock/OpenAIのクライアントを返す。"""
    if settings.llm_provider == "openai":
        return OpenAIClient(api_key=settings.openai_api_key, model=settings.openai_model)
    return BedrockClient(region=settings.bedrock_region, model_id=settings.bedrock_model_id)
