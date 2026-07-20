from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.review import Review


def add_review(db: Session, session_id: str, proposal: str, result: str) -> Review:
    review = Review(session_id=session_id, proposal=proposal, result=result)
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


def get_reviews(db: Session, session_id: str) -> list[Review]:
    stmt = (
        select(Review)
        .where(Review.session_id == session_id)
        .order_by(Review.created_at, Review.id)
    )
    return list(db.scalars(stmt))
