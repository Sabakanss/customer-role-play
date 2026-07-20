from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリ全体の設定。.env や環境変数から読み込む。"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM切り替え: "bedrock" または "openai"
    llm_provider: str = "bedrock"

    # Amazon Bedrock
    bedrock_region: str = "us-east-1"
    bedrock_model_id: str = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # DB
    database_url: str = "sqlite:///./app/db/app.db"


settings = Settings()

# セッション識別用Cookie名（api/chat.py, main.py で共通利用）
SESSION_COOKIE_NAME = "session_id"
