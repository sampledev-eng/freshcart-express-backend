from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from .. import models, schemas, utils
from ..db import get_db
from ..config import settings
import os
import uuid
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])


def authenticate_user(db: Session, email: str, password: str):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return False
    if not utils.verify_password(password, user.hashed_password):
        return False
    return user

@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(minutes=settings.refresh_token_expire_minutes)
    access_token = utils.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    refresh_token = utils.create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh", response_model=schemas.Token)
def refresh_token(token: schemas.TokenData, db: Session = Depends(get_db)):
    from jose import JWTError, jwt
    try:
        payload = jwt.decode(token.token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        jti: str = payload.get("jti")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if utils.is_token_blacklisted(db, jti):
            raise HTTPException(status_code=401, detail="Token revoked")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    refresh_token_expires = timedelta(minutes=settings.refresh_token_expire_minutes)
    access_token = utils.create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    new_refresh_token = utils.create_refresh_token(data={"sub": user.email}, expires_delta=refresh_token_expires)
    db.add(models.BlacklistedToken(jti=jti))
    db.commit()
    return {"access_token": access_token, "refresh_token": new_refresh_token}


@router.post("/forgot-password")
def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    code = str(uuid.uuid4()).split("-")[0]
    user.reset_code = code
    db.commit()
    # Here we would send email via SMTP
    return {"detail": "OTP sent"}


@router.post("/reset-password")
def reset_password(email: EmailStr, code: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email, models.User.reset_code == code).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid code")
    user.hashed_password = utils.get_password_hash(new_password)
    user.reset_code = None
    db.commit()
    return {"detail": "password updated"}


@router.post("/logout")
def logout(token: schemas.TokenData, db: Session = Depends(get_db)):
    db_token = models.BlacklistedToken(jti=token.token)
    db.add(db_token)
    db.commit()
    return {"detail": "logged out"}


@router.put("/profile", response_model=schemas.User)
def update_profile(profile: schemas.User, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == profile.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.profile_image = profile.profile_image
    db.commit()
    db.refresh(user)
    return user


@router.post("/profile/image", response_model=schemas.User)
def upload_image(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    os.makedirs("media", exist_ok=True)
    file_path = f"media/{uuid.uuid4().hex}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    user.profile_image = file_path
    db.commit()
    db.refresh(user)
    return user
