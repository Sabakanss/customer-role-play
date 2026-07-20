# 設計ドキュメント

「何を作ったか」「なぜそう作ったか」をまとめたドキュメントです。

---

## 1. 全体像

AI顧客役にヒアリングし、まとめた改善提案を提出すると、同じAI顧客が現場責任者の視点でレビューを返す、
という2画面のWebアプリです。

```
ブラウザ
 ├─ /chat   … AI顧客とヒアリングするチャット画面
 └─ /review … 改善提案を提出してレビューをもらう画面
```

裏側では FastAPI がリクエストを受け、SQLiteに会話・レビュー履歴を保存しながら、
Amazon Bedrock（Claude Haiku）またはOpenAI APIを呼び出してAI顧客の応答を生成します。

---

## 2. ディレクトリ構成と役割

```text
app/
├── main.py                 # FastAPIアプリ本体。ルーティングの集約場所
├── config.py                # 環境変数(.env)から設定を読み込む
│
├── api/                     # HTTPの入り口（リクエスト/レスポンスの形だけを扱う）
│   ├── chat.py               # POST /chat
│   └── review.py             # POST /review
│
├── services/                 # 業務ロジック（「何をするか」を組み立てる層）
│   ├── chat_service.py        # セッション開始・チャット処理
│   ├── review_service.py      # レビュー処理
│   └── prompt_service.py      # シナリオ+プロンプトテンプレートの組み立て
│
├── llm/                       # LLM呼び出しの抽象化（Bedrock/OpenAI切り替え）
│   ├── base.py                 # 共通インターフェース(LLMClient)
│   ├── bedrock_client.py       # Amazon Bedrock実装
│   ├── openai_client.py        # OpenAI実装
│   └── factory.py              # 設定に応じてどちらかを返す
│
├── repositories/              # DBアクセスだけを担当する層
│   ├── session_repository.py
│   ├── message_repository.py
│   └── review_repository.py
│
├── models/                    # DBテーブル定義（SQLAlchemy）
│   ├── database.py             # engine/セッション/テーブル作成
│   ├── session.py              # ChatSessionテーブル
│   ├── message.py              # Messageテーブル
│   └── review.py               # Reviewテーブル
│
├── prompts/                   # LLMに渡すシステムプロンプトのテンプレート(Jinja2)
│   ├── customer.md              # ヒアリング時の人格・振る舞いルール
│   └── review.md                # レビュー時の評価観点
│
├── scenarios/
│   └── sample_cafe.yaml        # シナリオ定義の例（顧客像・隠し情報・制約・レビュー観点）
│
├── utils/
│   ├── scenario_loader.py      # シナリオYAMLを読み込んでPydanticモデルに変換
│   └── prompt_loader.py        # prompts/配下のJinja2テンプレートを描画する汎用関数
│
├── templates/                  # 画面のHTML(Jinja2)
│   ├── chat.html
│   └── review.html
│
├── static/
│   ├── css/style.css
│   └── js/{chat.js, review.js}  # fetch()でAPIを呼ぶだけの素のJS
│
└── db/app.db                    # SQLiteファイル（.gitignore対象）
```

### レイヤーを分けた理由

`api/`（入出力の形） → `services/`（何をするか） → `repositories/`（DB操作） → `models/`（テーブル定義）
と責務を分けています。理由は、たとえば「LLMプロバイダを差し替える」「DBをSQLiteからPostgreSQLに変える」
といった変更が起きても、影響範囲を1層に閉じ込められるためです。

---

## 3. 主要な設計判断とその理由

### 3.1 `ChatSession` という命名（`Session`にしなかった理由）

`app/models/session.py` のORMクラスは `ChatSession` という名前にしています。
SQLAlchemyには既に `sqlalchemy.orm.Session`（DBとの接続・トランザクションを表すクラス）があり、
同じ「Session」という名前を使うと、同じファイル内で2つの意味の異なる`Session`が混在して読みにくくなるためです。

### 3.2 LLMラッパー（`llm/`）の抽象化

`llm/base.py` に `LLMClient` という抽象クラスを定義し、`chat(system_prompt, messages) -> str` という
共通インターフェースだけを決めています。`bedrock_client.py` と `openai_client.py` はこれを実装するだけで、
呼び出し側（`chat_service.py` など）はどちらを使っているか意識しません。
`factory.py` が `.env` の `LLM_PROVIDER` を見てどちらのインスタンスを返すか決めます。

### 3.3 Bedrockのモデル指定について

Amazon Bedrockでは、モデルによって「モデルIDを直接指定できるもの」と
「クロスリージョン推論プロファイルID（`us.` などの接頭辞が付いたID）でしか呼び出せないもの」があります。
本プロジェクトのデフォルト値（`app/config.py`）は動作確認済みのプロファイルIDを設定していますが、
利用するAWSアカウント・リージョンによって使えるモデル・IDの形式が異なるため、
`ResourceNotFoundException` や `ValidationException` が出た場合はAWSコンソールの
Bedrockモデルアクセス設定と、指定しているIDの形式を確認してください。

### 3.4 セッションはCookieで識別（ログイン機能なし）

ログイン機能は無く、`/chat` に初めてアクセスした際にサーバーが `session_id` というCookieを発行し、
それをDBの`sessions`テーブルの主キーと結び付けています。以後のリクエストはこのCookieでどのセッション
（＝どの会話）かを識別します。

### 3.5 「最初の発言」はLLMを呼ばずDBに直接保存する

`chat_service.start_session()` は、新しいセッションを作る際、シナリオYAMLの `opening_line` を
**LLMを呼ばずにそのままDBへ保存**します。

理由: プロンプト内で「最初はこう切り出してください」と指示していますが、これは会話の最初のターンにだけ
当てはまる指示です。もしLLM呼び出しで毎回この指示を送ると、2回目以降のやり取りでも初回発言を
繰り返してしまう可能性があります。最初の発言をDBに"種"として保存しておけば、2ターン目以降は会話履歴を
見てLLMが「もう言った」と判断できます。

### 3.6 `POST /chat` はセッションが無いとエラーを返す（自動作成しない）

セッションの作成・初回発言の保存は **`GET /chat`（画面表示時）** の責務とし、
`POST /chat`（チャット送信API）は「有効なセッションがある前提」のシンプルな処理に留めています。
Cookieが無い/無効な場合は400エラーを返します。

### 3.7 レビュー結果もDBに保存する（`reviews`テーブル）

`sessions` / `messages` に加えて `reviews`（提案内容・レビュー結果・日時）を用意し、
レビュー画面で過去の提案・レビューを一覧表示できるようにしています。

### 3.8 レビューの文体

レビュー結果が見出しや箇条書き、絵文字を使った「レポート」のような文体にならないよう、
`prompts/review.md` に「見出しや箇条書き、絵文字を使わず、自然な話し言葉で」という指示を入れています。
AI顧客というキャラクターが口頭で話しているように見えるよう、チャット画面のトーンと揃える狙いです。

### 3.9 シナリオはYAMLで差し替え可能

`app/scenarios/` にYAMLファイルを追加し、読み込み時のシナリオIDを変えるだけで別のシナリオに切り替えられます。
プロンプト（`prompts/customer.md`, `prompts/review.md`）側は `{{ scenario.xxx }}` という変数で
シナリオの内容を参照するだけで、業種や役職に依存したハードコードを持たないようにしています。
画面のラベル表示（「〇〇からのレビュー」等）もシナリオの `customer_role` を動的に埋め込んでおり、
別業種のシナリオに差し替えても表示が破綻しないようにしています。

---

## 4. データの流れ

### 4.1 ヒアリング（`GET /chat` → `POST /chat`）

```
1. ブラウザが GET /chat にアクセス
2. Cookieが無ければ:
   - sessionsテーブルに新規セッションを作成
   - シナリオのopening_lineをmessagesテーブルに assistant発言として保存
3. これまでの会話履歴をDBから取得し、chat.htmlに埋め込んで返す（Cookieもセット）
4. ユーザーが入力欄にメッセージを送信 → JS(chat.js)がfetchで POST /chat
5. サーバー側 (chat_service.send_message):
   a. 履歴取得 (messages テーブルから session_id で絞り込み)
   b. シナリオ取得
   c. システムプロンプト生成 (prompts/customer.md をJinja2で描画)
   d. LLM呼び出し (履歴 + 新規メッセージを渡す)
   e. ユーザー発言・AI応答の両方をmessagesテーブルに保存
   f. 応答をJSONで返す
6. JSがレスポンスを画面に追加表示
```

### 4.2 レビュー（`GET /review` → `POST /review`）

```
1. ブラウザが GET /review にアクセス（セッション無ければ /chat にリダイレクト）
2. これまでのレビュー履歴（あれば）を表示
3. ユーザーが改善提案を送信 → JS(review.js)がfetchで POST /review
4. サーバー側 (review_service.review_proposal):
   a. シナリオ取得
   b. システムプロンプト生成 (prompts/review.md)
   c. LLM呼び出し（提案文をuserメッセージとして渡す。会話履歴は使わず単発評価）
   d. 提案とレビュー結果をreviewsテーブルに保存
   e. 結果をJSONで返す
5. JSがレビュー結果を画面に追加表示
```

---

## 5. 現在の状態

* ヒアリング（`/chat`）、レビュー（`/review`）ともにブラウザで一連の流れが動作することを確認済み
* Bedrock / OpenAI いずれも `LLM_PROVIDER` の切り替えで動作する設計
* 自動テストは未整備（動作確認は手動 / スクリプトで実施）

## 6. 今後の拡張候補

* Docker対応
* 複数シナリオの切り替えUI
* pytestによる自動テスト
* AWS（ECS等）へのデプロイ
