from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.meeting import MeetingCreate, MeetingResponse
from app.crud.meeting import create_meeting

router = APIRouter()


@router.post("/generate", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED, tags=["Meetings"])
def generate_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    """Create a new meeting record from raw meeting text and summary."""
    if not meeting.title or not meeting.raw_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="title and raw_text are required"
        )

    try:
        created_meeting = create_meeting(db, meeting)
        return created_meeting
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to create meeting: {exc}"
        )
