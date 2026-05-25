from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ActionItemBase(BaseModel):
    task: str = Field(..., example="Send follow-up email")
    owner: Optional[str] = Field(None, example="Jane Doe")
    due_date: Optional[datetime] = Field(None, example="2026-06-01T00:00:00Z")
    status: Optional[str] = Field("pending", example="pending")


class ActionItemUpdate(BaseModel):
    task: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None


class ActionItemResponse(ActionItemBase):
    id: int
    meeting_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
