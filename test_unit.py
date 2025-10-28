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
# Import the module, not the variables directly
import todo_app

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
    # Reset before test
    todo_app.reset_database()
    yield
    # Reset after test (cleanup)
    todo_app.reset_database()


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
    
    Returns:
        list: The populated todos_db list
    """
    # Make sure database is empty first
    todo_app.reset_database()
    
    # Add test data
    todo_app.todos_db.append(sample_todo)
    todo_app.todos_db.append({
        "id": 2,
        "title": "Write integration tests",
        "description": "Test API endpoints",
        "priority": "medium",
        "completed": False,
        "created_at": datetime.now().isoformat()
    })
    
    yield todo_app.todos_db
    
    # Cleanup after test
    todo_app.reset_database()


# ============================================================================
# UNIT TESTS FOR generate_id()
# ============================================================================

class TestGenerateId:
    """
    Test suite for the generate_id() function.
    
    What we're testing:
    - ID generation starts at 1
    - IDs increment sequentially
    - Multiple calls produce unique IDs
    """
    
    def test_first_id_is_one(self):
        """
        Test that the first generated ID is 1.
        
        Expected behavior:
        - First call to generate_id() returns 1
        
        Why this matters:
        - Ensures predictable starting point
        - Important for database consistency
        """
        # Act: Call the function
        result = todo_app.generate_id()
        
        # Assert: Check the result
        assert result == 1, "First ID should be 1"
    
    
    def test_id_increments_sequentially(self):
        """
        Test that IDs increment by 1 each time.
        
        Expected behavior:
        - Each call returns the next sequential number
        
        Why this matters:
        - Prevents ID collisions
        - Ensures uniqueness
        """
        # Act: Generate multiple IDs
        id1 = todo_app.generate_id()
        id2 = todo_app.generate_id()
        id3 = todo_app.generate_id()
        
        # Assert: Check they increment
        assert id1 == 1, "First ID should be 1"
        assert id2 == 2, "Second ID should be 2"
        assert id3 == 3, "Third ID should be 3"
    
    
    def test_ids_are_unique(self):
        """
        Test that all generated IDs are unique.
        
        Expected behavior:
        - No duplicate IDs in a series of calls
        
        Why this matters:
        - Duplicate IDs would corrupt the database
        - Critical for data integrity
        """
        # Act: Generate 10 IDs
        ids = [todo_app.generate_id() for _ in range(10)]
        
        # Assert: Check uniqueness
        assert len(ids) == len(set(ids)), "All IDs should be unique"
        assert len(ids) == 10, "Should generate 10 IDs"


# ============================================================================
# UNIT TESTS FOR find_todo_by_id()
# ============================================================================

class TestFindTodoById:
    """
    Test suite for the find_todo_by_id() function.
    
    What we're testing:
    - Finding existing todos returns correct item
    - Finding non-existent todos returns None
    - Correct matching logic
    """
    
    def test_finds_existing_todo(self, populated_db):
        """
        Test that existing TODOs can be found by ID.
        
        Expected behavior:
        - Returns the correct TODO item
        - All fields match the original
        """
        # Act: Find TODO with ID 1
        result = todo_app.find_todo_by_id(1)
        
        # Assert: Check it was found and is correct
        assert result is not None, "Should find existing TODO"
        assert result["id"] == 1, "Should return TODO with matching ID"
        assert result["title"] == "Write unit tests", "Should return correct TODO"
    
    
    def test_returns_none_for_nonexistent_id(self):
        """
        Test that non-existent IDs return None.
        
        Expected behavior:
        - Returns None (not an error)
        - Handles missing data gracefully
        
        Why this matters:
        - Allows caller to handle "not found" case
        - Prevents crashes on invalid IDs
        """
        # Act: Try to find non-existent TODO
        result = todo_app.find_todo_by_id(999)
        
        # Assert: Check it returns None
        assert result is None, "Should return None for non-existent ID"
    
    
    def test_finds_correct_todo_among_many(self, populated_db):
        """
        Test that the correct TODO is returned when multiple exist.
        
        Expected behavior:
        - Returns exactly the requested TODO
        - Doesn't return wrong TODO
        """
        # Act: Find specific TODO
        result = todo_app.find_todo_by_id(2)
        
        # Assert: Check it's the right one
        assert result is not None, "Should find the TODO"
        assert result["id"] == 2, "Should return TODO with ID 2"
        assert result["title"] == "Write integration tests", "Should return correct TODO"
        assert result["id"] != 1, "Should not return wrong TODO"


# ============================================================================
# UNIT TESTS FOR reset_database()
# ============================================================================

class TestResetDatabase:
    """
    Test suite for the reset_database() function.
    
    What we're testing:
    - Database is cleared
    - ID counter is reset
    - Can be called multiple times safely
    """
    
    def test_clears_all_todos(self, populated_db):
        """
        Test that reset_database() clears all TODO items.
        
        Expected behavior:
        - todos_db becomes empty list
        - All data is removed
        """
        # Arrange: Verify database has data
        assert len(todo_app.todos_db) > 0, "Database should have data before reset"
        
        # Act: Reset the database
        todo_app.reset_database()
        
        # Assert: Check it's empty
        assert len(todo_app.todos_db) == 0, "Database should be empty after reset"
    
    
    def test_resets_id_counter(self, populated_db):
        """
        Test that reset_database() resets the ID counter.
        
        Expected behavior:
        - Next generated ID is 1 again
        - Counter restarts from beginning
        
        Why this matters:
        - Ensures consistent test environment
        - Prevents ID exhaustion in tests
        """
        # Arrange: Generate some IDs
        todo_app.generate_id()
        todo_app.generate_id()
        
        # Act: Reset database
        todo_app.reset_database()
        
        # Assert: Check next ID is 1
        next_id_after_reset = todo_app.generate_id()
        assert next_id_after_reset == 1, "ID counter should reset to 1"
    
    
    def test_can_be_called_multiple_times(self):
        """
        Test that reset_database() can be called repeatedly without errors.
        
        Expected behavior:
        - No errors when called on empty database
        - Idempotent operation (same result regardless of how many times called)
        """
        # Act: Reset multiple times
        todo_app.reset_database()
        todo_app.reset_database()
        todo_app.reset_database()
        
        # Assert: Check final state is correct
        assert len(todo_app.todos_db) == 0, "Database should still be empty"
        assert todo_app.generate_id() == 1, "ID counter should be at 1"


# ============================================================================
# TEST EXECUTION INFO
# ============================================================================

"""
HOW TO RUN THESE TESTS:
-----------------------

1. Install pytest:
   pip install pytest

2. Run all tests:
   pytest test_unit.py -v

3. Run specific test class:
   pytest test_unit.py::TestGenerateId -v

4. Run specific test:
   pytest test_unit.py::TestGenerateId::test_first_id_is_one -v

5. Run with coverage:
   pytest test_unit.py --cov=todo_app --cov-report=html


UNDERSTANDING TEST OUTPUT:
--------------------------
✓ PASSED - Test succeeded
✗ FAILED - Test failed (shows what went wrong)
s SKIPPED - Test was skipped
x XFAIL - Expected failure (test is known to fail)


WHAT MAKES A GOOD UNIT TEST:
-----------------------------
1. FAST - Runs in milliseconds
2. ISOLATED - No dependencies on external systems
3. REPEATABLE - Same result every time
4. SELF-VALIDATING - Clear pass/fail (no manual inspection)
5. TIMELY - Written before or with the code
"""
