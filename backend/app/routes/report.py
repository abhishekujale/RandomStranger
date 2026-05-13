# app/routes/report.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.database import get_db
from app.models import Report, Chat
from app.schemas import ReportCreate, ReportOut

router = APIRouter()


@router.post("/", response_model=ReportOut)
async def create_report(data: ReportCreate, db: AsyncSession = Depends(get_db)):
    """
    User reports their chat partner.
    Saves to DB so moderators can review.
    """
    # Make sure the chat actually exists
    chat_result = await db.execute(select(Chat).where(Chat.id == data.chat_id))
    if not chat_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Chat not found")

    report = Report(
        id=str(uuid.uuid4()),
        chat_id=data.chat_id,
        reporter_id=data.reporter_id,
        reason=data.reason,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/", response_model=list[ReportOut])
async def list_reports(db: AsyncSession = Depends(get_db)):
    """
    Get all reports — for a future moderation dashboard.
    In production you'd add authentication so only admins can call this.
    """
    result = await db.execute(select(Report).order_by(Report.created_at.desc()))
    return result.scalars().all()