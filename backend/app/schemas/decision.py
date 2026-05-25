from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class DecisionBase(BaseModel):
    decision_text: str = Field(..., example="Approve the Q3 roadmap.")


class DecisionResponse(DecisionBase):
    id: int
    meeting_id: int

    model_config = {
        "from_attributes": True
    }
