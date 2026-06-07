from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db import get_db
from app.models.entities import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    settings = get_settings()
    subject = decode_access_token(token, settings.secret_key)
    if not subject:
        raise HTTPException(status_code=401, detail='Invalid authentication token')
    user = db.query(User).filter(User.id == int(subject)).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    return user
