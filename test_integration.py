"""
Integration Tests for TODO API
================================
Integration tests verify that different parts work together correctly.

Test Framework: pytest + FastAPI TestClient
Test Type: Integration Testing (API Testing)
Coverage: All API endpoints

Author: Testing Demo
Date: October 2025
"""

import pytest
from fastapi.testclient import TestClient
from todo_app import app, reset_database

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def reset_before_test():
    """Automatically reset database before each test."""
    reset_database()
    yield


@pytest.fixture
def client():
    """Create a TestClient for making HTTP requests."""
    return TestClient(app)


# ============================================================================
# TESTS FOR ROOT ENDPOINT
# ============================================================================

class TestRootEndpoint:
    """Test suite for the root (/) endpoint."""
    
    def test_root_returns_welcome_message(self, client):
        """Test that root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"


# ============================================================================
# TESTS FOR GET /todos
# ============================================================================

class TestGetTodos:
    """Test suite for GET /todos endpoint."""
    
    def test_get_todos_returns_empty_list_initially(self, client):
        """Test that GET /todos returns empty list when no TODOs exist."""
        response = client.get("/todos")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_get_todos_returns_created_todos(self, client):
        """Test that GET /todos returns all created TODO items."""
        client.post("/todos", json={"title": "Test 1", "priority": "high"})
        client.post("/todos", json={"title": "Test 2", "priority": "low"})
        
        response = client.get("/todos")
        assert response.status_code == 200
        todos = response.json()
        assert len(todos) == 2
        assert todos[0]["title"] == "Test 1"
        assert todos[1]["title"] == "Test 2"
    
    def test_get_todos_filter_by_completed(self, client):
        """Test filtering TODOs by completion status."""
        client.post("/todos", json={"title": "Todo 1"})
        client.post("/todos", json={"title": "Todo 2"})
        client.put("/todos/1", json={"completed": True})
        
        response_completed = client.get("/todos?completed=true")
        response_incomplete = client.get("/todos?completed=false")
        
        completed_todos = response_completed.json()
        incomplete_todos = response_incomplete.json()
        
        assert len(completed_todos) == 1
        assert completed_todos[0]["completed"] is True
        assert len(incomplete_todos) == 1
        assert incomplete_todos[0]["completed"] is False


# ============================================================================
# TESTS FOR POST /todos
# ============================================================================

class TestCreateTodo:
    """Test suite for POST /todos endpoint."""
    
    def test_create_todo_with_valid_data(self, client):
        """Test creating a TODO with valid data."""
        todo_data = {
            "title": "Write documentation",
            "description": "Document all API endpoints",
            "priority": "high"
        }
        
        response = client.post("/todos", json=todo_data)
        assert response.status_code == 201
        
        created_todo = response.json()
        assert created_todo["id"] == 1
        assert created_todo["title"] == todo_data["title"]
        assert created_todo["completed"] is False
        assert "created_at" in created_todo
    
    def test_create_todo_with_minimal_data(self, client):
        """Test creating TODO with only required fields."""
        todo_data = {"title": "Simple TODO"}
        response = client.post("/todos", json=todo_data)
        
        assert response.status_code == 201
        created_todo = response.json()
        assert created_todo["title"] == "Simple TODO"
        assert created_todo["priority"] == "medium"
    
    def test_create_todo_with_invalid_priority(self, client):
        """Test that invalid priority values are rejected."""
        todo_data = {"title": "Test", "priority": "super-urgent"}
        response = client.post("/todos", json=todo_data)
        assert response.status_code == 422


# ============================================================================
# TESTS FOR GET /todos/{id}
# ============================================================================

class TestGetTodoById:
    """Test suite for GET /todos/{id} endpoint."""
    
    def test_get_existing_todo(self, client):
        """Test retrieving an existing TODO by ID."""
        create_response = client.post("/todos", json={"title": "Test TODO"})
        todo_id = create_response.json()["id"]
        
        response = client.get(f"/todos/{todo_id}")
        assert response.status_code == 200
        todo = response.json()
        assert todo["id"] == todo_id
        assert todo["title"] == "Test TODO"
    
    def test_get_nonexistent_todo_returns_404(self, client):
        """Test that requesting non-existent TODO returns 404."""
        response = client.get("/todos/999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ============================================================================
# TESTS FOR PUT /todos/{id}
# ============================================================================

class TestUpdateTodo:
    """Test suite for PUT /todos/{id} endpoint."""
    
    def test_update_todo_title(self, client):
        """Test updating a TODO's title."""
        create_response = client.post("/todos", json={"title": "Original"})
        todo_id = create_response.json()["id"]
        
        response = client.put(f"/todos/{todo_id}", json={"title": "Updated"})
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"
    
    def test_mark_todo_as_completed(self, client):
        """Test marking a TODO as completed."""
        create_response = client.post("/todos", json={"title": "Test"})
        todo_id = create_response.json()["id"]
        
        response = client.put(f"/todos/{todo_id}", json={"completed": True})
        assert response.status_code == 200
        assert response.json()["completed"] is True


# ============================================================================
# TESTS FOR DELETE /todos/{id}
# ============================================================================

class TestDeleteTodo:
    """Test suite for DELETE /todos/{id} endpoint."""
    
    def test_delete_existing_todo(self, client):
        """Test deleting an existing TODO."""
        create_response = client.post("/todos", json={"title": "To Delete"})
        todo_id = create_response.json()["id"]
        
        response = client.delete(f"/todos/{todo_id}")
        assert response.status_code == 204
        
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 404


"""
HOW TO RUN:
-----------
pytest test_integration.py -v
"""
