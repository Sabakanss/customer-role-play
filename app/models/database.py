from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    """テーブル未作成なら作成する。モデルをimportしてBaseに登録してから呼ぶ。"""
    from app.models import message, review, session  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPIの依存性注入で使うDBセッション。リクエスト終了時に必ずcloseする。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
