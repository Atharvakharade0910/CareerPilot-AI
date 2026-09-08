import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.dialects.postgresql import insert
from app.services.arbeitnow import fetch_page
from sqlalchemy import select
from sqlalchemy.orm import Session as DB
from app.core.database import get_db
from app.core.security import current_user
from app.models.entities import User, Job, JobMatch, CandidateFact, ResumeVersion, CandidateProfile, Application, AuditLog
from app.services.matching import score_job, aggregate_gaps
from app.services.jobs_provider import search_adzuna

router = APIRouter(prefix="/api")
SEED = [
 {"external_id":"meridian-junior-ai","company":"Meridian Labs","title":"Junior AI Engineer","location":"Bengaluru","work_type":"hybrid","experience_level":"entry","salary":"₹8–12 LPA","requirements":{"required":["Python","FastAPI","RAG","PostgreSQL"],"preferred":["Docker","AWS"]},"description":"Build Python AI services with FastAPI, RAG and PostgreSQL."},
 {"external_id":"forma-genai","company":"Forma Intelligence","title":"GenAI Engineer","location":"Remote, India","work_type":"remote","experience_level":"entry","salary":"₹10–16 LPA","requirements":{"required":["Python","LangGraph","Large Language Models","RAG"],"preferred":["AWS","Docker"]},"description":"Prototype grounded LLM applications and evaluation workflows."},
 {"external_id":"northstar-ml","company":"Northstar Analytics","title":"Machine Learning Engineer","location":"Pune","work_type":"hybrid","experience_level":"entry","salary":"₹7–11 LPA","requirements":{"required":["Python","Scikit-learn","SQL"],"preferred":["Docker","CI/CD"]},"description":"Ship reproducible machine learning services with Python and SQL."},
 {"external_id":"canopy-applied-ai","company":"Canopy Systems","title":"Applied AI Engineer","location":"Mumbai","work_type":"onsite","experience_level":"entry","salary":"₹8–14 LPA","requirements":{"required":["FastAPI","PostgreSQL","RAG"],"preferred":["AWS","Kubernetes"]},"description":"Deliver applied AI features with APIs, retrieval and cloud tooling."},
 {"external_id":"orbit-nlp","company":"Orbit Research","title":"NLP Engineer","location":"Remote, India","work_type":"remote","experience_level":"entry","salary":"₹9–14 LPA","requirements":{"required":["Python","NLP","Large Language Models"],"preferred":["Docker","LangChain"]},"description":"Build language systems and evaluation pipelines."},
]
def ensure_jobs(db):
    if not db.scalar(select(Job.id).limit(1)):
        db.add_all([Job(source="curated-demo", **x) for x in SEED]); db.commit()
def j(job): return {"id":str(job.id),"company":job.company,"title":job.title,"location":job.location,"work_type":job.work_type,"experience_level":job.experience_level,"salary":job.salary,"source":job.source,"requirements":job.requirements,"description":job.description,"posted_at":job.posted_at}
def latest(db,user): return db.scalar(select(ResumeVersion).where(ResumeVersion.user_id==user.id).order_by(ResumeVersion.created_at.desc()))
def profile(db,user): return db.scalar(select(CandidateProfile).where(CandidateProfile.user_id==user.id))
def facts(db,user,resume): return [{"value":f.value,"category":f.category,"accepted":f.accepted} for f in db.scalars(select(CandidateFact).where(CandidateFact.user_id==user.id,CandidateFact.resume_id==resume.id))]

@router.get("/jobs")
def jobs(q:str="", remote:bool=False, db:DB=Depends(get_db), user:User=Depends(current_user)):
    ensure_jobs(db); rows=list(db.scalars(select(Job).where(Job.active==True).order_by(Job.posted_at.desc())))
    if q: rows=[x for x in rows if q.lower() in f"{x.title} {x.company} {x.description}".lower()]
    if remote: rows=[x for x in rows if x.work_type=="remote"]
    return [j(x) for x in rows]
@router.get("/jobs/search/live")
async def live_jobs(q:str=Query("", max_length=120), location:str=Query("", max_length=120), page:int=Query(1, ge=1, le=20), remote:bool=False, db:DB=Depends(get_db)):
    try:
        rows, fetched, stale, more = await fetch_page(page)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
    for row in rows:
        stmt = insert(Job).values(**row)
        db.execute(stmt.on_conflict_do_update(constraint="uq_job_source_external",
                   set_={key: getattr(stmt.excluded, key) for key in row if key not in ("source", "external_id")}))
    db.commit()
    ids = [row["external_id"] for row in rows]
    stored = db.scalars(select(Job).where(Job.source=="arbeitnow", Job.external_id.in_(ids)).order_by(Job.posted_at.desc())).all()
    filtered = [x for x in stored if q.casefold() in f"{x.title} {x.company} {x.description}".casefold()
                and location.casefold() in x.location.casefold() and (not remote or x.work_type=="remote")]
    return {"provider":"arbeitnow", "results":[dict(j(x), url=x.url) for x in filtered],
            "page":page, "has_more":more and page < 20, "fetched_at":fetched, "stale":stale}
@router.get("/jobs/{job_id}")
def detail(job_id:uuid.UUID,db:DB=Depends(get_db),user:User=Depends(current_user)):
    ensure_jobs(db); x=db.get(Job,job_id)
    if not x: raise HTTPException(404,"Opportunity not found.")
    return j(x)
@router.post("/jobs/{job_id}/match")
def match(job_id:uuid.UUID,db:DB=Depends(get_db),user:User=Depends(current_user)):
    ensure_jobs(db); x=db.get(Job,job_id); r=latest(db,user)
    if not x or not r: raise HTTPException(422,"Upload and review a resume before matching.")
    result=score_job(profile(db,user).preferences,facts(db,user,r),j(x));
    existing=db.scalar(select(JobMatch).where(JobMatch.user_id==user.id,JobMatch.job_id==x.id,JobMatch.resume_id==r.id))
    if existing: existing.score=result["score"]; existing.breakdown=result
    else: db.add(JobMatch(user_id=user.id,job_id=x.id,resume_id=r.id,score=result["score"],breakdown=result))
    db.commit()
    return {"job":j(x),**result,"category":"Excellent Match" if result["score"]>=85 else "Strong Match" if result["score"]>=75 else "Moderate Match" if result["score"]>=60 else "Weak Match"}
@router.get("/skills/gaps")
def gaps(db:DB=Depends(get_db),user:User=Depends(current_user)):
    ensure_jobs(db);r=latest(db,user)
    if not r:return {"jobs_analyzed":0,"gaps":[]}
    rows=[score_job(profile(db,user).preferences,facts(db,user,r),j(x)) for x in db.scalars(select(Job).where(Job.active==True))]
    return {"jobs_analyzed":len(rows),"minimum_jobs":5,"gaps":aggregate_gaps(rows)}
@router.post("/applications")
def save_application(job_id:uuid.UUID,db:DB=Depends(get_db),user:User=Depends(current_user)):
    x=db.get(Job,job_id);r=latest(db,user)
    if not x or not r:raise HTTPException(422,"A valid job and resume are required.")
    existing=db.scalar(select(Application).where(Application.user_id==user.id,Application.job_id==x.id))
    if existing:return {"id":str(existing.id),"status":existing.status}
    a=Application(user_id=user.id,job_id=x.id,resume_id=r.id,status="saved");db.add(a);db.add(AuditLog(user_id=user.id,event="application.saved",details={"job_id":str(x.id)}));db.commit();return {"id":str(a.id),"status":a.status}
@router.get("/applications")
def list_applications(db:DB=Depends(get_db),user:User=Depends(current_user)):
    return [{"id":str(a.id),"job_id":str(a.job_id),"status":a.status,"created_at":a.created_at,"notes":a.notes} for a in db.scalars(select(Application).where(Application.user_id==user.id).order_by(Application.created_at.desc()))]

@router.get("/saved-jobs")
def saved_jobs(db:DB=Depends(get_db),user:User=Depends(current_user)):
    rows=db.execute(select(Application,Job).join(Job,Application.job_id==Job.id).where(Application.user_id==user.id).order_by(Application.created_at.desc())).all()
    return [{"application_id":str(a.id),"saved_at":a.created_at,"status":a.status,"job":dict(j(job),url=job.url)} for a,job in rows]
