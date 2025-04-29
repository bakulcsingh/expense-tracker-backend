from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BudgetBase(BaseModel):
    amount: float = Field(..., gt=0)
    name: str
    description: Optional[str] = None
    start_date: datetime
    end_date: datetime
    category_id: Optional[int] = None  # None for overall budget

class BudgetCreate(BudgetBase):
    pass

class BudgetUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    category_id: Optional[int] = None

class BudgetInDB(BudgetBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Budget(BudgetInDB):
    """Budget representation for API responses"""
    pass

class BudgetProgress(BaseModel):
    budget_id: int
    budget_name: str
    budget_amount: float
    spent_amount: float
    remaining_amount: float
    percentage_used: float
    start_date: datetime
    end_date: datetime
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    is_exceeded: bool