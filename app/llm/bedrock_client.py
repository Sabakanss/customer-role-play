import boto3

from app.llm.base import LLMClient


class BedrockClient(LLMClient):
    def __init__(self, region: str, model_id: str) -> None:
        self._client = boto3.client("bedrock-runtime", region_name=region)
        self._model_id = model_id

    def chat(self, system_prompt: str, messages: list[dict[str, str]]) -> str:
        response = self._client.converse(
            modelId=self._model_id,
            system=[{"text": system_prompt}],
            messages=[
                {"role": m["role"], "content": [{"text": m["content"]}]}
                for m in messages
            ],
        )
        return response["output"]["message"]["content"][0]["text"]
