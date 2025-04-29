from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.category import Category, CategoryCreate, CategoryUpdate
from app.schemas.user import User
from app.services.category import get_categories, get_category, create_category, update_category, delete_category
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)

@router.get("/", response_model=List[Category])
async def read_categories(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all categories for the current user"""
    return get_categories(db, current_user.id, skip, limit)

@router.get("/{category_id}", response_model=Category)
async def read_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific category by ID"""
    return get_category(db, category_id, current_user.id)

@router.post("/", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_new_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new category"""
    return create_category(db, category_data, current_user.id)

@router.put("/{category_id}", response_model=Category)
async def update_existing_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing category"""
    return update_category(db, category_id, category_data, current_user.id)

@router.delete("/{category_id}")
async def delete_existing_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a category"""
    return delete_category(db, category_id, current_user.id)