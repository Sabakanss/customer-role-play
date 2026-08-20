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

    # アプリの公開URL（末尾スラッシュなし）。Cognitoのコールバック/サインアウトURL登録時にも使う
    app_base_url: str = "http://127.0.0.1:8000"

    # Cookie署名用の秘密鍵。本番では十分ランダムな文字列を環境変数で設定すること
    session_secret_key: str = "dev-insecure-secret-change-me"
    # 本番(https)ではTrue固定。ローカル(http)開発時のみ.envでFalseにする
    secure_cookies: bool = True

    # Amazon Cognito（ユーザー認証）
    cognito_region: str = "us-east-1"
    cognito_user_pool_id: str = ""
    cognito_client_id: str = ""
    cognito_client_secret: str = ""
    # 例: https://your-app.auth.us-east-1.amazoncognito.com
    cognito_domain: str = ""


settings = Settings()

# セッション識別用Cookie名（api/chat.py, main.py で共通利用）
SESSION_COOKIE_NAME = "session_id"
