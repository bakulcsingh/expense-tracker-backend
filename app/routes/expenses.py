from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.schemas.expense import (
    Expense, ExpenseCreate, ExpenseUpdate, 
    ExpenseSummary, CategoryExpenseSummary, TimePeriodExpenseSummary
)
from app.schemas.user import User
from app.services.expense import (
    get_expenses, get_expense, create_expense, update_expense, delete_expense,
    get_expense_summary, get_expenses_by_category, get_monthly_expenses
)
from app.utils.security import get_current_user

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)

@router.get("/", response_model=List[Expense])
async def read_expenses(
    skip: int = 0, 
    limit: int = 100,
    category_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get expenses for the current user with optional filters"""
    return get_expenses(
        db, current_user.id, skip, limit, 
        category_id=category_id, 
        start_date=start_date, 
        end_date=end_date
    )

@router.get("/summary", response_model=ExpenseSummary)
async def read_expense_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get expense summary statistics"""
    return get_expense_summary(db, current_user.id, start_date, end_date)

@router.get("/by-category", response_model=List[CategoryExpenseSummary])
async def read_expenses_by_category(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get expenses grouped by category"""
    return get_expenses_by_category(db, current_user.id, start_date, end_date)

@router.get("/monthly", response_model=List[TimePeriodExpenseSummary])
async def read_monthly_expenses(
    months: int = Query(12, ge=1, le=60),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly expense summaries"""
    return get_monthly_expenses(db, current_user.id, months)

@router.get("/{expense_id}", response_model=Expense)
async def read_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense by ID"""
    return get_expense(db, expense_id, current_user.id)

@router.post("/", response_model=Expense, status_code=status.HTTP_201_CREATED)
async def create_new_expense(
    expense_data: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    return create_expense(db, expense_data, current_user.id)

@router.put("/{expense_id}", response_model=Expense)
async def update_existing_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing expense"""
    return update_expense(db, expense_id, expense_data, current_user.id)

@router.delete("/{expense_id}")
async def delete_existing_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    return delete_expense(db, expense_id, current_user.id)