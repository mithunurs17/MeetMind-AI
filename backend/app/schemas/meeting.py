from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.action_item import ActionItemBase, ActionItemResponse
from app.schemas.decision import DecisionBase, DecisionResponse
from app.schemas.risk import RiskBase, RiskResponse


class MeetingBase(BaseModel):
    title: str = Field(..., example="Project Kickoff")
    raw_text: str = Field(..., example="The meeting covered product roadmap and next steps...")
    summary: Optional[str] = Field(None, example="Summary of meeting topics and decisions.")


class MeetingCreate(MeetingBase):
    action_items: Optional[List[ActionItemBase]] = None
    decisions: Optional[List[DecisionBase]] = None
    risks: Optional[List[RiskBase]] = None


class MeetingAIRequest(BaseModel):
    title: Optional[str] = Field(None, example="Project Kickoff")
    raw_text: str = Field(..., example="The meeting covered product roadmap and next steps...")


class MeetingResponse(MeetingBase):
    id: int
    created_at: datetime
    action_items: List[ActionItemResponse] = []
    decisions: List[DecisionResponse] = []
    risks: List[RiskResponse] = []
    open_questions: List[str] = []

    model_config = {
        "from_attributes": True
    }
