import hashlib, uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DB
from app.core.database import get_db
from app.core.security import current_user
from app.models.entities import User, ResumeVersion, CandidateFact, Job, Application, TailoredResume, ApplicationApproval, Notification
from app.services.resume_parser import validate_claim
from app.services.gemini import generate, GeminiUnavailable

router=APIRouter(prefix="/api")
def latest(db,u): return db.scalar(select(ResumeVersion).where(ResumeVersion.user_id==u.id).order_by(ResumeVersion.created_at.desc()))
def facts(db,u,r): return list(db.scalars(select(CandidateFact).where(CandidateFact.user_id==u.id,CandidateFact.resume_id==r.id,CandidateFact.accepted==True)))
@router.post('/resume/tailor')
def tailor(job_id:uuid.UUID,db:DB=Depends(get_db),user:User=Depends(current_user)):
    r=latest(db,user); job=db.get(Job,job_id)
    if not r or not job: raise HTTPException(422,'A reviewed resume and valid job are required.')
    accepted=facts(db,user,r); evidence=[{'id':str(f.id),'value':f.value,'evidence':f.evidence} for f in accepted]
    content={'summary':f"Candidate profile aligned to {job.title} at {job.company} using verified resume evidence.",'highlighted_facts':[x['value'] for x in evidence], 'evidence_ids':[x['id'] for x in evidence]}
    validation={'passed':True,'claims':[{'claim':x['value'],'evidence_id':x['id'],'valid':validate_claim(x['value'],x['evidence'],r.text)} for x in evidence], 'resume_version_id':str(r.id)}
    validation['passed'] = bool(validation['claims']) and all(claim['valid'] for claim in validation['claims'])
    tr=TailoredResume(user_id=user.id,resume_id=r.id,job_id=job.id,content=content,validation=validation);db.add(tr);db.commit();return {'id':str(tr.id),'content':content,'validation':validation,'status':'draft'}
@router.post('/applications/{application_id}/approve')
def approve(application_id:uuid.UUID,db:DB=Depends(get_db),user:User=Depends(current_user)):
    a=db.scalar(select(Application).where(Application.id==application_id,Application.user_id==user.id));r=latest(db,user)
    if not a or not r:raise HTTPException(404,'Application or resume not found.')
    digest=hashlib.sha256(f'{a.id}:{r.id}:{a.answers}'.encode()).hexdigest(); existing=db.scalar(select(ApplicationApproval).where(ApplicationApproval.application_id==a.id))
    if existing: existing.resume_id=r.id;existing.approved=True;existing.approved_at=datetime.now(timezone.utc);existing.content_hash=digest
    else:db.add(ApplicationApproval(application_id=a.id,user_id=user.id,resume_id=r.id,content_hash=digest,approved=True,approved_at=datetime.now(timezone.utc)))
    a.status='approved';db.commit();return {'id':str(a.id),'status':a.status,'approval_hash':digest}
@router.get('/notifications')
def notifications(db:DB=Depends(get_db),user:User=Depends(current_user)):
    return [{'id':str(n.id),'kind':n.kind,'title':n.title,'message':n.message,'read':n.read,'link':n.link,'created_at':n.created_at} for n in db.scalars(select(Notification).where(Notification.user_id==user.id).order_by(Notification.created_at.desc()).limit(50))]
@router.post('/notifications/{notification_id}/read')
def read(notification_id:uuid.UUID,db:DB=Depends(get_db),user:User=Depends(current_user)):
    n=db.scalar(select(Notification).where(Notification.id==notification_id,Notification.user_id==user.id))
    if not n:raise HTTPException(404,'Notification not found.')
    n.read=True;db.commit();return {'ok':True}
@router.post('/assistant')
async def assistant(query:str,db:DB=Depends(get_db),user:User=Depends(current_user)):
    r=latest(db,user)
    if not r:return {'provider':'local','message':'Upload and review your resume first so I can ground advice in your evidence.','evidence_ids':[]}
    terms=query.lower(); all_facts=facts(db,user,r); values=[f.value for f in all_facts]
    if 'skill gap' in terms or 'learn' in terms:
        return {'provider':'local','message':'Your local workspace can now analyze recurring gaps after five relevant roles. Live market analysis and learning resources require the next connector phase.','evidence_ids':[str(f.id) for f in all_facts]}
    try:
        msg = await generate(f"Accepted resume evidence: {values[:20]}\nUser question: {query}\nAnswer concisely and only from the evidence. If evidence is insufficient, say so.")
        return {'provider':'gemini','message':msg,'evidence_ids':[str(f.id) for f in all_facts[:20]]}
    except GeminiUnavailable:
        return {'provider':'local','message':f'I can ground this workspace in your reviewed resume. Current accepted evidence includes: {", ".join(values[:8]) or "no structured facts yet"}. Gemini is temporarily unavailable, so this is the local fallback.','evidence_ids':[str(f.id) for f in all_facts[:8]]}
