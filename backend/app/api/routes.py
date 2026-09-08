import hashlib, uuid
from pathlib import Path
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    Request,
    UploadFile,
    File,
)
from fastapi.responses import FileResponse
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session as DB
from app.core.database import get_db
from app.core.config import settings
from app.core.security import current_user, passwords, establish, digest
from app.models.entities import (
    User,
    Session,
    CandidateProfile,
    ResumeVersion,
    CandidateFact,
    AuditLog,
)
from app.schemas.profile import Registration, Credentials, ProfileUpdate
from app.services.resume_parser import document_text, extract

router = APIRouter(prefix="/api")


def public(user):
    return {"id": str(user.id), "email": user.email, "full_name": user.full_name}


def profile_for(db, user):
    return db.scalar(
        select(CandidateProfile).where(CandidateProfile.user_id == user.id)
    )


def latest(db, user):
    return db.scalar(
        select(ResumeVersion)
        .where(ResumeVersion.user_id == user.id)
        .order_by(ResumeVersion.created_at.desc())
    )


@router.post("/auth/register", status_code=201)
def register(data: Registration, response: Response, db: DB = Depends(get_db)):
    user = User(
        email=data.email.lower(),
        full_name=data.full_name.strip(),
        password_hash=passwords.hash(data.password),
    )
    db.add(user)
    try:
        db.flush()
        db.add(
            CandidateProfile(user_id=user.id, personal={"full_name": user.full_name, "gender": data.gender})
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "An account with this email already exists.")
    establish(db, user, response)
    return public(user)


@router.post("/auth/login")
def login(data: Credentials, response: Response, db: DB = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    check = user.password_hash if user else DUMMY_HASH
    valid = passwords.verify(data.password, check)
    if not user or not valid:
        raise HTTPException(401, "Email or password is incorrect.")
    establish(db, user, response)
    return public(user)


DUMMY_HASH = passwords.hash("unusable-dummy-password")


@router.get("/auth/me")
def me(user: User = Depends(current_user)):
    return public(user)


@router.post("/auth/logout")
def logout(request: Request, response: Response, db: DB = Depends(get_db)):
    db.execute(
        delete(Session).where(
            Session.token_hash == digest(request.cookies.get("careerpilot_session", ""))
        )
    )
    db.commit()
    response.delete_cookie("careerpilot_session", path="/")
    return {"ok": True}


@router.post("/auth/forgot-password")
def forgot():
    raise HTTPException(
        503,
        "Password recovery email is not configured. Contact your deployment administrator.",
    )


@router.get("/profile")
def profile(db: DB = Depends(get_db), user: User = Depends(current_user)):
    p = profile_for(db, user)
    r = latest(db, user)
    return {
        "personal": p.personal,
        "preferences": p.preferences,
        "reviewed": p.reviewed,
        "resume": (
            {
                "id": str(r.id),
                "filename": r.filename,
                "extraction": r.extraction,
                "text": r.text,
            }
            if r
            else None
        ),
    }


@router.put("/profile")
def update_profile(
    data: ProfileUpdate, db: DB = Depends(get_db), user: User = Depends(current_user)
):
    p = profile_for(db, user)
    if data.reviewed and not latest(db, user):
        raise HTTPException(422, "Upload a resume before completing review.")
    p.personal = data.personal.model_dump()
    p.preferences = data.preferences.model_dump()
    p.reviewed = data.reviewed
    if data.personal.full_name.strip():
        user.full_name = data.personal.full_name.strip()
    db.add(
        AuditLog(
            user_id=user.id,
            event="profile.reviewed" if data.reviewed else "profile.updated",
        )
    )
    db.commit()
    return {"ok": True}


@router.patch("/profile/facts/{fact_id}")
def review_fact(
    fact_id: uuid.UUID,
    accepted: bool,
    db: DB = Depends(get_db),
    user: User = Depends(current_user),
):
    fact = db.scalar(
        select(CandidateFact).where(
            CandidateFact.id == fact_id, CandidateFact.user_id == user.id
        )
    )
    if not fact:
        raise HTTPException(404, "Fact not found.")
    fact.accepted = accepted
    db.commit()
    return {"ok": True}


@router.get("/profile/facts")
def facts(db: DB = Depends(get_db), user: User = Depends(current_user)):
    r = latest(db, user)
    if not r:
        return []
    return [
        {
            "id": str(f.id),
            "value": f.value,
            "category": f.category,
            "evidence": f.evidence,
            "accepted": f.accepted,
        }
        for f in db.scalars(
            select(CandidateFact).where(
                CandidateFact.user_id == user.id, CandidateFact.resume_id == r.id
            )
        )
    ]


@router.post("/resume/upload", status_code=201)
def upload(
    file: UploadFile = File(...),
    db: DB = Depends(get_db),
    user: User = Depends(current_user),
):
    data = file.file.read(5 * 1024 * 1024 + 1)
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(413, "Resume must be 5 MB or smaller.")
    name = Path((file.filename or "resume").replace("\\", "/")).name[:255]
    try:
        text = document_text(data, name)
        parsed = extract(text)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except Exception:
        raise HTTPException(
            422, "Could not read this document. Please export a new PDF or DOCX."
        )
    key = str(uuid.uuid4()) + Path(name).suffix.lower()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    path = settings.storage_dir / key
    path.write_bytes(data)
    try:
        r = ResumeVersion(
            user_id=user.id,
            filename=name,
            storage_key=key,
            sha256=hashlib.sha256(data).hexdigest(),
            text=text,
            extraction=parsed.model_dump(),
        )
        db.add(r)
        db.flush()
        for f in parsed.fields:
            db.add(
                CandidateFact(
                    user_id=user.id,
                    resume_id=r.id,
                    category=f.category,
                    value=f.value,
                    evidence=f.evidence,
                )
            )
        profile_for(db, user).reviewed = False
        db.add(
            AuditLog(
                user_id=user.id,
                event="resume.parsed",
                details={
                    "resume_id": str(r.id),
                    "field_count": len(parsed.fields),
                    "parser": parsed.parser,
                },
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        path.unlink(missing_ok=True)
        raise
    return {
        "id": str(r.id),
        "filename": name,
        "extraction": parsed.model_dump(),
        "text": text,
    }


@router.get("/resume/versions")
def versions(db: DB = Depends(get_db), user: User = Depends(current_user)):
    return [
        {
            "id": str(r.id),
            "filename": r.filename,
            "created_at": r.created_at,
            "parser": r.parser,
        }
        for r in db.scalars(
            select(ResumeVersion)
            .where(ResumeVersion.user_id == user.id)
            .order_by(ResumeVersion.created_at.desc())
        )
    ]


@router.get("/resume/{resume_id}/download")
def download(
    resume_id: uuid.UUID, db: DB = Depends(get_db), user: User = Depends(current_user)
):
    r = db.scalar(
        select(ResumeVersion).where(
            ResumeVersion.id == resume_id, ResumeVersion.user_id == user.id
        )
    )
    if not r:
        raise HTTPException(404, "Resume not found.")
    return FileResponse(settings.storage_dir / r.storage_key, filename=r.filename)


@router.get("/analytics/overview")
def overview(db: DB = Depends(get_db), user: User = Depends(current_user)):
    p = profile_for(db, user)
    r = latest(db, user)
    count = (
        len(
            list(
                db.scalars(
                    select(CandidateFact).where(
                        CandidateFact.user_id == user.id,
                        CandidateFact.resume_id == r.id,
                        CandidateFact.accepted == True,
                    )
                )
            )
        )
        if r
        else 0
    )
    return {
        "profile_completeness": sum(
            [
                25 if r else 0,
                25 if p.reviewed else 0,
                25 if p.preferences.get("target_roles") else 0,
                25 if p.personal.get("location") else 0,
            ]
        ),
        "facts": count,
        "jobs": 0,
        "applications": 0,
        "interviews": 0,
    }


@router.get("/notifications")
def notifications(db: DB = Depends(get_db), user: User = Depends(current_user)):
    return [
        {"id": str(a.id), "event": a.event, "created_at": a.created_at}
        for a in db.scalars(
            select(AuditLog)
            .where(AuditLog.user_id == user.id)
            .order_by(AuditLog.created_at.desc())
            .limit(20)
        )
    ]
