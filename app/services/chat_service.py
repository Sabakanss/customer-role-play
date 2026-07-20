from sqlalchemy.orm import Session as DBSession

from app.llm.factory import get_llm_client
from app.repositories import message_repository, session_repository
from app.services.prompt_service import build_customer_system_prompt
from app.utils.scenario_loader import load_scenario


def start_session(db: DBSession) -> tuple[str, str]:
    """新しいセッションを作成し、シナリオの初回発言を最初のassistantメッセージとして保存する。"""
    scenario = load_scenario()
    chat_session = session_repository.create_session(db, scenario_id=scenario.id)
    message_repository.add_message(db, chat_session.id, "assistant", scenario.opening_line)
    return chat_session.id, scenario.opening_line


def send_message(db: DBSession, session_id: str, user_message: str) -> str:
    """ユーザー発言を受け取り、履歴取得→プロンプト生成→LLM呼び出し→履歴保存を行い、応答を返す。"""
    scenario = load_scenario()
    system_prompt = build_customer_system_prompt(scenario)

    history = message_repository.get_messages(db, session_id)
    llm_messages = [{"role": m.role, "content": m.content} for m in history]
    llm_messages.append({"role": "user", "content": user_message})

    client = get_llm_client()
    reply = client.chat(system_prompt, llm_messages)

    message_repository.add_message(db, session_id, "user", user_message)
    message_repository.add_message(db, session_id, "assistant", reply)

    return reply


def get_history(db: DBSession, session_id: str) -> list[dict[str, str]]:
    messages = message_repository.get_messages(db, session_id)
    return [{"role": m.role, "content": m.content} for m in messages]
