from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import current_user
from app.models.entities import MockInterview, MockInterviewTurn, User
from app.services.gemini import generate, GeminiUnavailable

router = APIRouter(prefix="/api/mock-interviews", tags=["mock-interviews"])
class ScheduleIn(BaseModel):
    target_role: str = Field(min_length=2, max_length=180)
    scheduled_at: datetime
    timezone: str = "UTC"
    difficulty: str = "mixed"
    question_count: int = Field(default=5, ge=3, le=12)
class AnswerIn(BaseModel): answer: str = Field(min_length=1, max_length=12000)
def view(i, db):
    ts = db.scalars(select(MockInterviewTurn).where(MockInterviewTurn.interview_id == i.id).order_by(MockInterviewTurn.turn_index)).all()
    return {"id": str(i.id), "target_role": i.target_role, "scheduled_at": i.scheduled_at.isoformat(), "timezone": i.timezone, "difficulty": i.difficulty, "question_count": i.question_count, "status": i.status, "score": i.score, "feedback": i.feedback, "turns": [{"question": t.question, "answer": t.answer, "feedback": t.feedback} for t in ts]}
@router.get("")
def listing(user: User = Depends(current_user), db: Session = Depends(get_db)): return [view(i, db) for i in db.scalars(select(MockInterview).where(MockInterview.user_id == user.id).order_by(MockInterview.scheduled_at.desc())).all()]
@router.post("")
def schedule(p: ScheduleIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    when = p.scheduled_at if p.scheduled_at.tzinfo else p.scheduled_at.replace(tzinfo=timezone.utc)
    if when <= datetime.now(timezone.utc): raise HTTPException(422, "Schedule the interview in the future.")
    i = MockInterview(user_id=user.id, target_role=p.target_role.strip(), scheduled_at=when, timezone=p.timezone, difficulty=p.difficulty, question_count=p.question_count); db.add(i); db.commit(); db.refresh(i); return view(i, db)
@router.post("/{interview_id}/start")
def start(interview_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    i = db.scalar(select(MockInterview).where(MockInterview.id == interview_id, MockInterview.user_id == user.id))
    if not i: raise HTTPException(404, "Interview not found")
    i.status="in_progress"; db.add(MockInterviewTurn(interview_id=i.id, turn_index=0, question=f"Tell me about your experience relevant to the {i.target_role} role.")); db.commit(); return view(i, db)
@router.post("/{interview_id}/answer")
async def answer(interview_id: UUID, p: AnswerIn, user: User = Depends(current_user), db: Session = Depends(get_db)):
    i=db.scalar(select(MockInterview).where(MockInterview.id==interview_id, MockInterview.user_id==user.id))
    if not i or i.status!="in_progress": raise HTTPException(409,"Interview is not in progress")
    ts=db.scalars(select(MockInterviewTurn).where(MockInterviewTurn.interview_id==i.id).order_by(MockInterviewTurn.turn_index)).all(); t=ts[-1]
    result={"score":min(100,max(20,len(p.answer.split())*2)),"strengths":["Specificity"],"improvements":["Add a measurable outcome"],"summary":"Clear answer; strengthen it with a concise result."}
    try: result=await generate(f"Role: {i.target_role}\nQuestion: {t.question}\nAnswer: {p.answer}\nReturn JSON score, strengths, improvements, summary.")
    except GeminiUnavailable: pass
    t.answer=p.answer; t.feedback=result
    if len(ts)>=i.question_count: i.status="completed"; i.score=float(result.get("score",0)); i.feedback=result
    else: db.add(MockInterviewTurn(interview_id=i.id, turn_index=len(ts), question=f"Describe a challenging situation you handled as a {i.target_role}, and what changed because of your actions."))
    db.commit(); db.refresh(i); return view(i, db)
@router.post("/{interview_id}/cancel")
def cancel(interview_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    i=db.scalar(select(MockInterview).where(MockInterview.id==interview_id, MockInterview.user_id==user.id))
    if not i: raise HTTPException(404,"Interview not found")
    i.status="cancelled"; db.commit(); return view(i, db)
