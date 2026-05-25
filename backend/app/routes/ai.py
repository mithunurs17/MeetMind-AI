from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.meeting import MeetingAIRequest, MeetingResponse
from app.services.ai_service import extract_structured_meeting
from app.crud.meeting import save_ai_generated

router = APIRouter()


@router.post(
    "/ai/extract",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI"],
)
def ai_extract(transcript: MeetingAIRequest, db: Session = Depends(get_db)):
    """Accept a JSON body with 'title' and 'raw_text' and run AI/NLP extraction."""
    if not transcript.raw_text:
        raise HTTPException(status_code=400, detail="raw_text is required")

    try:
        structured = extract_structured_meeting(transcript.raw_text, title=transcript.title)
        saved = save_ai_generated(db, structured)
        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/ai/extract-file",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["AI"],
)
def ai_extract_file(
    file: UploadFile = File(...),
    title: str | None = None,
    db: Session = Depends(get_db),
):
    """Upload a document (txt, pdf, docx, image) and run AI/NLP extraction."""
    try:
        from app.utils.ingest import extract_text_from_file

        raw_text = extract_text_from_file(file)
        if not raw_text:
            raise HTTPException(status_code=400, detail="Unable to extract text from uploaded file")

        structured = extract_structured_meeting(raw_text, title=title)
        saved = save_ai_generated(db, structured)
        return saved
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
