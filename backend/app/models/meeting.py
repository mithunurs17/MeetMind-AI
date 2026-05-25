from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Meeting(Base):
    """Meeting model for storing meeting information."""

    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    raw_text = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    action_items = relationship(
        "ActionItem",
        back_populates="meeting",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    decisions = relationship(
        "Decision",
        back_populates="meeting",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    risks = relationship(
        "Risk",
        back_populates="meeting",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    @property
    def open_questions(self):
        return [
            risk.risk_text.replace("OPEN QUESTION:", "").strip()
            for risk in self.risks
            if isinstance(risk.risk_text, str) and risk.risk_text.startswith("OPEN QUESTION:")
        ]
