from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

from app.models.budget import Budget
from app.models.category import Category
from app.models.expense import Expense
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetProgress

def get_budgets(db: Session, user_id: int, skip: int = 0, limit: int = 100, 
               active_only: bool = False):
    """Get budgets for a user"""
    query = db.query(Budget).filter(Budget.user_id == user_id)
    
    # Filter for active budgets if requested
    if active_only:
        query = query.filter(Budget.is_active == True)
    
    # Order by start date descending (newest first)
    query = query.order_by(Budget.start_date.desc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

def get_budget(db: Session, budget_id: int, user_id: int):
    """Get a specific budget by ID"""
    budget = db.query(Budget).filter(
        Budget.id == budget_id,
        Budget.user_id == user_id
    ).first()
    
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    return budget

def create_budget(db: Session, budget_data: BudgetCreate, user_id: int):
    """Create a new budget"""
    # If category_id is provided, verify it exists and belongs to the user
    if budget_data.category_id:
        category = db.query(Category).filter(
            Category.id == budget_data.category_id,
            Category.user_id == user_id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Validate dates
    if budget_data.start_date >= budget_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Create budget
    db_budget = Budget(
        **budget_data.dict(),
        user_id=user_id
    )
    
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    
    return db_budget

def update_budget(db: Session, budget_id: int, budget_data: BudgetUpdate, user_id: int):
    """Update an existing budget"""
    # Get existing budget
    db_budget = get_budget(db, budget_id, user_id)
    
    # Check if category_id is being updated and is valid
    if budget_data.category_id is not None and budget_data.category_id != db_budget.category_id:
        if budget_data.category_id:  # Skip check if setting to None
            category = db.query(Category).filter(
                Category.id == budget_data.category_id,
                Category.user_id == user_id
            ).first()
            
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Category not found"
                )
    
    # Validate dates if both are provided
    if budget_data.start_date and budget_data.end_date:
        if budget_data.start_date >= budget_data.end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
    
    # Update fields
    update_data = budget_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_budget, key, value)
    
    db.commit()
    db.refresh(db_budget)
    
    return db_budget

def delete_budget(db: Session, budget_id: int, user_id: int):
    """Delete a budget"""
    # Get existing budget
    db_budget = get_budget(db, budget_id, user_id)
    
    # Delete budget
    db.delete(db_budget)
    db.commit()
    
    return {"message": "Budget deleted successfully"}

def get_budget_progress(db: Session, budget_id: int, user_id: int):
    """Get progress information for a specific budget"""
    # Get budget
    budget = get_budget(db, budget_id, user_id)
    
    # Calculate total spending for this budget's period and category (if applicable)
    query = db.query(func.sum(Expense.amount)).filter(
        Expense.user_id == user_id,
        Expense.date >= budget.start_date,
        Expense.date <= budget.end_date
    )
    
    # Filter by category if the budget is category-specific
    if budget.category_id:
        query = query.filter(Expense.category_id == budget.category_id)
    
    spent_amount = query.scalar() or 0
    remaining_amount = budget.amount - spent_amount
    percentage_used = (spent_amount / budget.amount) * 100 if budget.amount > 0 else 0
    is_exceeded = spent_amount > budget.amount
    
    # Get category name if applicable
    category_name = None
    if budget.category_id:
        category = db.query(Category).filter(Category.id == budget.category_id).first()
        if category:
            category_name = category.name
    
    return BudgetProgress(
        budget_id=budget.id,
        budget_name=budget.name,
        budget_amount=budget.amount,
        spent_amount=spent_amount,
        remaining_amount=remaining_amount,
        percentage_used=percentage_used,
        start_date=budget.start_date,
        end_date=budget.end_date,
        category_id=budget.category_id,
        category_name=category_name,
        is_exceeded=is_exceeded
    )

def get_all_budget_progress(db: Session, user_id: int, active_only: bool = True):
    """Get progress information for all budgets"""
    # Get budgets
    budgets = get_budgets(db, user_id, active_only=active_only)
    
    result = []
    for budget in budgets:
        progress = get_budget_progress(db, budget.id, user_id)
        result.append(progress)
    
    return result