from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.routes import auth, users, categories, expenses, budgets

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Expense Tracker API",
    description="API for tracking personal expenses, categorizing spending, and managing budgets",
    version="1.0.0",
)

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Next.js development server
    "http://localhost:8000",
    # Add production URLs when deployed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(budgets.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Expense Tracker API. Visit /docs for API documentation."}

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connection"""
    try:
        # Simple database query to check connection
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}