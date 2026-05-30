from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.meeting import save_ai_generated
from app.database import get_db
from app.models.user import User
from app.schemas.meeting import MeetingAIRequest, MeetingResponse
from app.services.ai_service import extract_structured_meeting

router = APIRouter()


@router.post(
    "/ai/extract",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI"],
    summary="Extract meeting minutes from pasted text",
)
def ai_extract(
    transcript: MeetingAIRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not transcript.raw_text:
        raise HTTPException(400, "raw_text is required")
    try:
        structured = extract_structured_meeting(
            transcript.raw_text,
            title=transcript.title,
        )
        saved = save_ai_generated(db, structured, owner_id=current_user.id)
        return saved
    except Exception as exc:
        raise HTTPException(500, str(exc))


@router.post(
    "/ai/extract-file",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI"],
    summary="Extract meeting minutes from an uploaded file",
)
def ai_extract_file(
    file: UploadFile = File(...),
    # Declare title as an explicit Form field so FastAPI reads it from
    # the multipart body rather than dropping it.
    title: str = Form(default=""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        from app.utils.ingest import extract_text_from_file
        raw_text = extract_text_from_file(file)
        if not raw_text:
            raise HTTPException(400, "Unable to extract text from uploaded file")

        # Use the caller-supplied title; fall back gracefully if empty.
        meeting_title = title.strip() if title and title.strip() else None

        structured = extract_structured_meeting(raw_text, title=meeting_title)
        saved = save_ai_generated(db, structured, owner_id=current_user.id)
        return saved
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, str(exc))