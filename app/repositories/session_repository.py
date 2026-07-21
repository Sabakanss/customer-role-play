from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.session import ChatSession


def create_session(db: Session, scenario_id: str = "sample_cafe") -> ChatSession:
    chat_session = ChatSession(scenario_id=scenario_id)
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    return chat_session


def get_session(db: Session, session_id: str) -> ChatSession | None:
    return db.get(ChatSession, session_id)


def list_sessions(db: Session) -> list[ChatSession]:
    stmt = select(ChatSession).order_by(ChatSession.created_at.desc())
    return list(db.scalars(stmt))
