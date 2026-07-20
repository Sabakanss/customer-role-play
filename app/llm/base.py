from abc import ABC, abstractmethod


class LLMClient(ABC):
    """OpenAI / Bedrockを切り替えられるようにするための共通インターフェース。"""

    @abstractmethod
    def chat(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        """messages: [{"role": "user"|"assistant", "content": str}, ...] の会話履歴を渡し、応答テキストを返す。"""
        raise NotImplementedError
