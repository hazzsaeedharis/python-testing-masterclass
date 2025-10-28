"""
Unit Tests for TODO API
========================
Unit tests focus on testing individual functions and components in isolation.

Test Framework: pytest
Test Type: Unit Testing
Coverage: Helper functions and business logic

Author: Testing Demo
Date: October 2025
"""

import pytest
from datetime import datetime
from todo_app import (
    generate_id, 
    find_todo_by_id, 
    reset_database,
    todos_db,
    next_id
)

# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def reset_db_before_each_test():
    """
    Fixture that automatically runs before each test.
    Ensures clean database state for every test.
    
    Why this matters:
    - Tests should be independent
    - No test should affect another test's results
    - Clean slate = reliable tests
    """
    reset_database()
    yield


@pytest.fixture
def sample_todo():
    """
    Fixture that provides a sample TODO item for testing.
    
    Returns:
        dict: A complete TODO item with all fields
    """
    return {
        "id": 1,
        "title": "Write unit tests",
        "description": "Create comprehensive test suite",
        "priority": "high",
        "completed": False,
        "created_at": datetime.now().isoformat()
    }


@pytest.fixture
def populated_db(sample_todo):
    """
    Fixture that populates the database with test data.
    """
    todos_db.append(sample_todo)
    todos_db.append({
        "id": 2,
        "title": "Write integration tests",
        "description": "Test API endpoints",
        "priority": "medium",
        "completed": False,
        "created_at": datetime.now().isoformat()
    })
    return todos_db


# ============================================================================
# UNIT TESTS FOR generate_id()
# ============================================================================

class TestGenerateId:
    """Test suite for the generate_id() function."""
    
    def test_first_id_is_one(self):
        """Test that the first generated ID is 1."""
        result = generate_id()
        assert result == 1, "First ID should be 1"
    
    def test_id_increments_sequentially(self):
        """Test that IDs increment by 1 each time."""
        id1 = generate_id()
        id2 = generate_id()
        id3 = generate_id()
        
        assert id1 == 1, "First ID should be 1"
        assert id2 == 2, "Second ID should be 2"
        assert id3 == 3, "Third ID should be 3"
    
    def test_ids_are_unique(self):
        """Test that all generated IDs are unique."""
        ids = [generate_id() for _ in range(10)]
        assert len(ids) == len(set(ids)), "All IDs should be unique"


# ============================================================================
# UNIT TESTS FOR find_todo_by_id()
# ============================================================================

class TestFindTodoById:
    """Test suite for the find_todo_by_id() function."""
    
    def test_finds_existing_todo(self, populated_db):
        """Test that existing TODOs can be found by ID."""
        result = find_todo_by_id(1)
        assert result is not None, "Should find existing TODO"
        assert result["id"] == 1
        assert result["title"] == "Write unit tests"
    
    def test_returns_none_for_nonexistent_id(self):
        """Test that non-existent IDs return None."""
        result = find_todo_by_id(999)
        assert result is None, "Should return None for non-existent ID"
    
    def test_finds_correct_todo_among_many(self, populated_db):
        """Test that the correct TODO is returned when multiple exist."""
        result = find_todo_by_id(2)
        assert result is not None
        assert result["id"] == 2
        assert result["title"] == "Write integration tests"


# ============================================================================
# UNIT TESTS FOR reset_database()
# ============================================================================

class TestResetDatabase:
    """Test suite for the reset_database() function."""
    
    def test_clears_all_todos(self, populated_db):
        """Test that reset_database() clears all TODO items."""
        assert len(todos_db) > 0, "Database should have data before reset"
        reset_database()
        assert len(todos_db) == 0, "Database should be empty after reset"
    
    def test_resets_id_counter(self, populated_db):
        """Test that reset_database() resets the ID counter."""
        generate_id()
        generate_id()
        reset_database()
        next_id_after_reset = generate_id()
        assert next_id_after_reset == 1, "ID counter should reset to 1"
    
    def test_can_be_called_multiple_times(self):
        """Test that reset_database() can be called repeatedly."""
        reset_database()
        reset_database()
        reset_database()
        assert len(todos_db) == 0
        assert generate_id() == 1


"""
HOW TO RUN THESE TESTS:
-----------------------
1. Install pytest: pip install pytest
2. Run all tests: pytest test_unit.py -v
3. Run with coverage: pytest test_unit.py --cov=todo_app
"""
