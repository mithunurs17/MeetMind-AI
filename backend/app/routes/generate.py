"""generate.py — Direct meeting creation (no AI extraction)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.meeting import create_meeting
from app.database import get_db
from app.models.user import User
from app.schemas.meeting import MeetingCreate, MeetingResponse

router = APIRouter()


@router.post(
    "/generate",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Meetings"],
    summary="Create a meeting record directly (no AI extraction)",
)
def generate_meeting(
    meeting: MeetingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not meeting.title or not meeting.raw_text:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "title and raw_text are required")
    try:
        # Always assign to the currently authenticated user
        return create_meeting(db, meeting, owner_id=current_user.id)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Unable to create meeting: {exc}",
        )