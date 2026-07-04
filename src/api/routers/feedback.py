"""POST /api/feedback — feedback de usuarios en fase de user testing, sin login."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.deps import get_db
from src.api.schemas import FeedbackCreate, FeedbackResponse
from src.load.models import Feedback
from src.notify import notify_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)) -> FeedbackResponse:
    row = Feedback(
        feedback_type=payload.feedback_type,
        comment=payload.comment,
        email=payload.email,
        importance=payload.importance,
        consent_contact=payload.consent_contact,
        page_url=payload.page_url,
        route=payload.route,
        filters_json=payload.filters_json,
        user_agent=payload.user_agent,
        viewport=payload.viewport,
        referrer=payload.referrer,
        reward_status="pending" if payload.email else "none",
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    # notify_feedback nunca lanza — una falla de notificación no debe perder
    # un feedback que ya quedó guardado en la base de datos.
    notify_feedback(row.id, row.feedback_type, row.comment, row.email, row.importance)

    return FeedbackResponse(id=row.id, status=row.status, reward_status=row.reward_status)
