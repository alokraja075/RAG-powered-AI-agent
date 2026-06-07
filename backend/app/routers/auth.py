from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db import get_db
from app.models.entities import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse


router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/register', response_model=UserResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')
    user = User(email=payload.email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserResponse(id=user.id, email=user.email)


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    settings = get_settings()
    token = create_access_token(str(user.id), settings.secret_key, settings.access_token_expire_minutes)
    return TokenResponse(access_token=token)
