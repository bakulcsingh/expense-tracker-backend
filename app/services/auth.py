from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.utils.security import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate a user by email and password"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_user_token(user: User):
    """Create access token for a user"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}