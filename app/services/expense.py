from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from app.models.expense import Expense
from app.models.category import Category
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseSummary, CategoryExpenseSummary, TimePeriodExpenseSummary

def get_expenses(db: Session, user_id: int, skip: int = 0, limit: int = 100, 
                category_id: Optional[int] = None, start_date: Optional[datetime] = None, 
                end_date: Optional[datetime] = None):
    """Get expenses for a user with optional filters"""
    query = db.query(Expense).filter(Expense.user_id == user_id)
    
    # Apply filters if provided
    if category_id:
        query = query.filter(Expense.category_id == category_id)
    
    if start_date:
        query = query.filter(Expense.date >= start_date)
    
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    # Order by date descending (newest first)
    query = query.order_by(Expense.date.desc())
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()

def get_expense(db: Session, expense_id: int, user_id: int):
    """Get a specific expense by ID"""
    expense = db.query(Expense).filter(
        Expense.id == expense_id,
        Expense.user_id == user_id
    ).first()
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    
    return expense

def create_expense(db: Session, expense_data: ExpenseCreate, user_id: int):
    """Create a new expense"""
    # Verify the category exists and belongs to the user
    category = db.query(Category).filter(
        Category.id == expense_data.category_id,
        Category.user_id == user_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Create expense
    db_expense = Expense(
        **expense_data.dict(),
        user_id=user_id
    )
    
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

def update_expense(db: Session, expense_id: int, expense_data: ExpenseUpdate, user_id: int):
    """Update an existing expense"""
    # Get existing expense
    db_expense = get_expense(db, expense_id, user_id)
    
    # Check if category_id is being updated and is valid
    if expense_data.category_id and expense_data.category_id != db_expense.category_id:
        category = db.query(Category).filter(
            Category.id == expense_data.category_id,
            Category.user_id == user_id
        ).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    # Update fields
    update_data = expense_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_expense, key, value)
    
    db.commit()
    db.refresh(db_expense)
    
    return db_expense

def delete_expense(db: Session, expense_id: int, user_id: int):
    """Delete an expense"""
    # Get existing expense
    db_expense = get_expense(db, expense_id, user_id)
    
    # Delete expense
    db.delete(db_expense)
    db.commit()
    
    return {"message": "Expense deleted successfully"}

def get_expense_summary(db: Session, user_id: int, start_date: Optional[datetime] = None, 
                       end_date: Optional[datetime] = None):
    """Get expense summary statistics"""
    query = db.query(
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count"),
        func.avg(Expense.amount).label("average"),
        func.min(Expense.amount).label("min"),
        func.max(Expense.amount).label("max")
    ).filter(Expense.user_id == user_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Expense.date >= start_date)
    
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    result = query.first()
    
    if not result or result.count == 0:
        return ExpenseSummary(total=0, count=0, average=0)
    
    return ExpenseSummary(
        total=result.total,
        count=result.count,
        average=result.average,
        min=result.min,
        max=result.max
    )

def get_expenses_by_category(db: Session, user_id: int, start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None):
    """Get expense summary grouped by category"""
    query = db.query(
        Category.id.label("category_id"),
        Category.name.label("category_name"),
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count"),
        func.avg(Expense.amount).label("average"),
        func.min(Expense.amount).label("min"),
        func.max(Expense.amount).label("max")
    ).join(Category).filter(Expense.user_id == user_id)
    
    # Apply date filters if provided
    if start_date:
        query = query.filter(Expense.date >= start_date)
    
    if end_date:
        query = query.filter(Expense.date <= end_date)
    
    # Group by category
    query = query.group_by(Category.id, Category.name)
    
    # Order by total amount descending
    query = query.order_by(func.sum(Expense.amount).desc())
    
    results = query.all()
    
    return [
        CategoryExpenseSummary(
            category_id=result.category_id,
            category_name=result.category_name,
            total=result.total,
            count=result.count,
            average=result.average,
            min=result.min,
            max=result.max
        ) for result in results
    ]

def get_monthly_expenses(db: Session, user_id: int, months: int = 12):
    """Get monthly expense summaries for the last N months"""
    # Calculate start date (first day of month N months ago)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30 * months)
    
    query = db.query(
        extract('year', Expense.date).label('year'),
        extract('month', Expense.date).label('month'),
        func.sum(Expense.amount).label("total"),
        func.count(Expense.id).label("count"),
        func.avg(Expense.amount).label("average"),
        func.min(Expense.amount).label("min"),
        func.max(Expense.amount).label("max")
    ).filter(
        Expense.user_id == user_id,
        Expense.date >= start_date,
        Expense.date <= end_date
    )
    
    # Group by year and month
    query = query.group_by('year', 'month')
    
    # Order by year and month descending (newest first)
    query = query.order_by('year', 'month')
    
    results = query.all()
    
    return [
        TimePeriodExpenseSummary(
            period=f"{result.year}-{result.month:02d}",  # Format: YYYY-MM
            total=result.total,
            count=result.count,
            average=result.average,
            min=result.min,
            max=result.max
        ) for result in results
    ]