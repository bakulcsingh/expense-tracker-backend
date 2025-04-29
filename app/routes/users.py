from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user import create_user, update_user, deactivate_user
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    return create_user(db, user_data)

@router.put("/me", response_model=User)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's details"""
    return update_user(db, current_user.id, user_data)

@router.delete("/me", response_model=User)
async def deactivate_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate current user's account"""
    return deactivate_user(db, current_user.id)