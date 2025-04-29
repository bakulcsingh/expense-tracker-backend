from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.budget import Budget, BudgetCreate, BudgetUpdate, BudgetProgress
from app.schemas.user import User
from app.services.budget import (
    get_budgets, get_budget, create_budget, update_budget, delete_budget,
    get_budget_progress, get_all_budget_progress
)
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/budgets",
    tags=["budgets"]
)

@router.get("/", response_model=List[Budget])
async def read_budgets(
    skip: int = 0, 
    limit: int = 100,
    active_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budgets for the current user"""
    return get_budgets(db, current_user.id, skip, limit, active_only)

@router.get("/progress", response_model=List[BudgetProgress])
async def read_all_budget_progress(
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress information for all budgets"""
    return get_all_budget_progress(db, current_user.id, active_only)

@router.get("/{budget_id}", response_model=Budget)
async def read_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific budget by ID"""
    return get_budget(db, budget_id, current_user.id)

@router.get("/{budget_id}/progress", response_model=BudgetProgress)
async def read_budget_progress(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress information for a specific budget"""
    return get_budget_progress(db, budget_id, current_user.id)

@router.post("/", response_model=Budget, status_code=status.HTTP_201_CREATED)
async def create_new_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget"""
    return create_budget(db, budget_data, current_user.id)

@router.put("/{budget_id}", response_model=Budget)
async def update_existing_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing budget"""
    return update_budget(db, budget_id, budget_data, current_user.id)

@router.delete("/{budget_id}")
async def delete_existing_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a budget"""
    return delete_budget(db, budget_id, current_user.id)