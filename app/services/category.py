from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

def get_categories(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Get all categories for a user"""
    return db.query(Category).filter(Category.user_id == user_id).offset(skip).limit(limit).all()

def get_category(db: Session, category_id: int, user_id: int):
    """Get a specific category by ID"""
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category

def create_category(db: Session, category_data: CategoryCreate, user_id: int):
    """Create a new category"""
    # Check if category with same name exists for user
    existing = db.query(Category).filter(
        Category.name == category_data.name,
        Category.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    # Create new category
    db_category = Category(
        **category_data.dict(),
        user_id=user_id
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category

def update_category(db: Session, category_id: int, category_data: CategoryUpdate, user_id: int):
    """Update an existing category"""
    # Get existing category
    db_category = get_category(db, category_id, user_id)
    
    # Check if the new name already exists for another category
    if category_data.name and category_data.name != db_category.name:
        existing = db.query(Category).filter(
            Category.name == category_data.name,
            Category.user_id == user_id,
            Category.id != category_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
    
    # Update fields
    update_data = category_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category

def delete_category(db: Session, category_id: int, user_id: int):
    """Delete a category"""
    # Get existing category
    db_category = get_category(db, category_id, user_id)
    
    # Check if the category has any expenses
    if db_category.expenses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category that has expenses"
        )
    
    # Delete category
    db.delete(db_category)
    db.commit()
    
    return {"message": "Category deleted successfully"}