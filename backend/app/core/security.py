import hashlib, secrets
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session as DB
from pwdlib import PasswordHash
from app.core.database import get_db
from app.core.config import settings
from app.models.entities import Session, User

passwords = PasswordHash.recommended()


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


def establish(db: DB, user: User, response: Response):
    token = secrets.token_urlsafe(48)
    db.add(
        Session(
            user_id=user.id,
            token_hash=digest(token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
    )
    db.commit()
    response.set_cookie(
        "careerpilot_session",
        token,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        max_age=604800,
        path="/",
    )


def current_user(request: Request, db: DB = Depends(get_db)):
    token = request.cookies.get("careerpilot_session", "")
    session = db.scalar(
        select(Session).where(
            Session.token_hash == digest(token),
            Session.expires_at > datetime.now(timezone.utc),
        )
    )
    if not session:
        raise HTTPException(401, "Please sign in to continue.")
    user = db.get(User, session.user_id)
    if not user:
        raise HTTPException(401, "Session is invalid.")
    return user
