from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ExpenseBase(BaseModel):
    amount: float = Field(..., gt=0)
    description: Optional[str] = None
    date: datetime
    note: Optional[str] = None
    payment_method: Optional[str] = None
    category_id: int

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    date: Optional[datetime] = None
    note: Optional[str] = None
    payment_method: Optional[str] = None
    category_id: Optional[int] = None

class ExpenseInDB(ExpenseBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Expense(ExpenseInDB):
    """Expense representation for API responses"""
    pass

# For expense analytics and reporting
class ExpenseSummary(BaseModel):
    total: float
    count: int
    average: float
    min: Optional[float] = None
    max: Optional[float] = None

class CategoryExpenseSummary(ExpenseSummary):
    category_id: int
    category_name: str

class TimePeriodExpenseSummary(ExpenseSummary):
    period: str  # e.g., "2023-04" for monthly, "2023-W12" for weekly