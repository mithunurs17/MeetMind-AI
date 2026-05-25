from __future__ import annotations
from pydantic import BaseModel, Field


class RiskBase(BaseModel):
    risk_text: str = Field(..., example="Potential deadline delays due to vendor constraints.")


class RiskResponse(RiskBase):
    id: int
    meeting_id: int

    model_config = {
        "from_attributes": True
    }
