from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.message import Message


def add_message(db: Session, session_id: str, role: str, content: str) -> Message:
    message = Message(session_id=session_id, role=role, content=content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def get_messages(db: Session, session_id: str) -> list[Message]:
    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at, Message.id)
    )
    return list(db.scalars(stmt))


def count_messages(db: Session, session_id: str) -> int:
    stmt = select(func.count()).select_from(Message).where(Message.session_id == session_id)
    return db.scalar(stmt) or 0


def get_last_message(db: Session, session_id: str) -> Message | None:
    stmt = (
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc(), Message.id.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()
