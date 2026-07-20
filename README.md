# AI顧客ロールプレイ演習アプリ（デモ）

AI顧客役とヒアリングを行い、まとめた改善提案に対してレビューをもらう、という
要件定義の練習ができるWebアプリのデモ・テンプレートです。

FastAPI + Amazon Bedrock（または OpenAI API）の学習用に作成しました。
同梱のシナリオ（`app/scenarios/sample_cafe.yaml`）は架空の内容です。

## できること

* AI顧客（架空の店長キャラクター）とのヒアリングチャット
* まとめた改善提案の提出と、AI顧客からのレビュー
* シナリオはYAMLで定義（顧客像・隠し情報・制約・レビュー観点）し、差し替え可能

## セットアップ

依存関係のインストール（[uv](https://docs.astral.sh/uv/) を使用）:

```bash
uv sync
```

`.env` を作成:

```bash
cp .env.example .env
```

`LLM_PROVIDER` で `bedrock` / `openai` を切り替えます。Bedrockを使う場合はAWS認証情報（`aws configure` 等）が別途必要です。

## 起動

```bash
uv run uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/chat` でヒアリング画面が開きます。

> **Windows補足**: `uv run python` でスクリプトを直接実行し日本語を`print`すると文字化けする場合は `PYTHONUTF8=1 uv run python ...` を使ってください（HTTP経由の動作には影響しません）。

## シナリオを差し替える

`app/scenarios/` に新しいYAMLを追加し、`app/utils/scenario_loader.py` の `load_scenario` のデフォルト値
（または呼び出し側）を変更してください。スキーマは `sample_cafe.yaml` を参照してください。

```yaml
id: シナリオID
industry: 業種
customer_role: 顧客の役職
opening_line: 最初の発言
hidden_facts: [聞かれたら答える情報のリスト]
constraints: [提案が満たすべき制約のリスト]
review_criteria: [レビュー時の評価観点のリスト]
```

## 技術構成

* FastAPI / SQLAlchemy / SQLite / Jinja2
* LLM: Amazon Bedrock または OpenAI API（`.env` の `LLM_PROVIDER` で切り替え）
