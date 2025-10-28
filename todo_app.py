"""
TODO API Application - Main Module
===================================
A simple FastAPI application for managing TODO items.
This demonstrates unit testing, integration testing, and E2E testing.

Author: Testing Demo
Date: October 2025
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uvicorn

# Initialize FastAPI application
app = FastAPI(
    title="TODO API",
    description="A simple TODO API for testing demonstrations",
    version="1.0.0"
)

# ============================================================================
# DATA MODELS (Pydantic)
# ============================================================================

class TodoCreate(BaseModel):
    """
    Schema for creating a new TODO item.
    
    Attributes:
        title: The TODO title (required, 1-100 chars)
        description: Optional description of the task
        priority: Priority level (low, medium, high)
    """
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")


class TodoResponse(BaseModel):
    """
    Schema for TODO item responses.
    
    Attributes:
        id: Unique identifier
        title: The TODO title
        description: Optional description
        priority: Priority level
        completed: Completion status
        created_at: Creation timestamp
    """
    id: int
    title: str
    description: Optional[str]
    priority: str
    completed: bool
    created_at: str


class TodoUpdate(BaseModel):
    """
    Schema for updating a TODO item.
    All fields are optional to allow partial updates.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    completed: Optional[bool] = None


# ============================================================================
# IN-MEMORY DATABASE (for demonstration purposes)
# ============================================================================

# This simulates a database - in production, use PostgreSQL, MongoDB, etc.
todos_db: List[dict] = []
next_id: int = 1


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_id() -> int:
    """
    Generate a unique ID for a new TODO item.
    
    Returns:
        int: The next available ID
    """
    global next_id
    current_id = next_id
    next_id += 1
    return current_id


def find_todo_by_id(todo_id: int) -> Optional[dict]:
    """
    Find a TODO item by its ID.
    
    Args:
        todo_id: The ID to search for
        
    Returns:
        dict: The TODO item if found, None otherwise
    """
    for todo in todos_db:
        if todo["id"] == todo_id:
            return todo
    return None


def reset_database():
    """
    Reset the database to empty state.
    Useful for testing to ensure clean state between tests.
    """
    global todos_db, next_id
    todos_db = []
    next_id = 1


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - health check.
    
    Returns:
        dict: Welcome message and API status
    """
    return {
        "message": "Welcome to TODO API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/todos", response_model=List[TodoResponse], tags=["Todos"])
async def get_todos(completed: Optional[bool] = None):
    """
    Get all TODO items, optionally filtered by completion status.
    
    Query Parameters:
        completed: Filter by completion status (optional)
        
    Returns:
        List[TodoResponse]: List of TODO items
        
    Example:
        GET /todos - returns all todos
        GET /todos?completed=true - returns only completed todos
    """
    if completed is None:
        return todos_db
    
    # Filter by completion status
    filtered_todos = [todo for todo in todos_db if todo["completed"] == completed]
    return filtered_todos


@app.get("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def get_todo(todo_id: int):
    """
    Get a specific TODO item by ID.
    
    Path Parameters:
        todo_id: The ID of the TODO item
        
    Returns:
        TodoResponse: The TODO item
        
    Raises:
        HTTPException 404: If TODO not found
    """
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TODO with id {todo_id} not found"
        )
    
    return todo


@app.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED, tags=["Todos"])
async def create_todo(todo: TodoCreate):
    """
    Create a new TODO item.
    
    Request Body:
        TodoCreate: The TODO data
        
    Returns:
        TodoResponse: The created TODO item with ID and timestamp
        
    Status Code:
        201: Created successfully
    """
    # Create new TODO with generated ID and timestamp
    new_todo = {
        "id": generate_id(),
        "title": todo.title,
        "description": todo.description,
        "priority": todo.priority,
        "completed": False,  # New todos are always incomplete
        "created_at": datetime.now().isoformat()
    }
    
    # Add to database
    todos_db.append(new_todo)
    
    return new_todo


@app.put("/todos/{todo_id}", response_model=TodoResponse, tags=["Todos"])
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    """
    Update an existing TODO item.
    Supports partial updates - only provided fields are updated.
    
    Path Parameters:
        todo_id: The ID of the TODO to update
        
    Request Body:
        TodoUpdate: The fields to update
        
    Returns:
        TodoResponse: The updated TODO item
        
    Raises:
        HTTPException 404: If TODO not found
    """
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TODO with id {todo_id} not found"
        )
    
    # Update only provided fields
    update_data = todo_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        todo[field] = value
    
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Todos"])
async def delete_todo(todo_id: int):
    """
    Delete a TODO item.
    
    Path Parameters:
        todo_id: The ID of the TODO to delete
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException 404: If TODO not found
    """
    todo = find_todo_by_id(todo_id)
    
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"TODO with id {todo_id} not found"
        )
    
    # Remove from database
    todos_db.remove(todo)
    
    return None


# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Run the application with uvicorn
    # Host: 0.0.0.0 allows external access
    # Port: 8000 (default FastAPI port)
    # Reload: Auto-reload on code changes (dev only)
    uvicorn.run(
        "todo_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
