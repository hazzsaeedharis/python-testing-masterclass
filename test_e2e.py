"""
End-to-End (E2E) Tests for TODO API
====================================
E2E tests simulate real user interactions.

Test Framework: pytest + requests
Test Type: End-to-End Testing
Coverage: Complete user workflows

Author: Testing Demo
Date: October 2025
"""

import pytest
import requests
import time

BASE_URL = "http://localhost:8000"
REQUEST_TIMEOUT = 5


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_server_running() -> bool:
    """Check if the API server is running."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def clear_all_todos():
    """Clear all TODOs from the database."""
    try:
        response = requests.get(f"{BASE_URL}/todos", timeout=REQUEST_TIMEOUT)
        todos = response.json()
        for todo in todos:
            requests.delete(f"{BASE_URL}/todos/{todo['id']}", timeout=REQUEST_TIMEOUT)
    except Exception as e:
        print(f"Warning: Could not clear TODOs: {e}")


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def ensure_server_running():
    """Ensure server is running before tests start."""
    if not is_server_running():
        pytest.skip(
            f"Server is not running at {BASE_URL}. "
            "Start it with: python todo_app.py"
        )
    yield


@pytest.fixture(autouse=True)
def clean_database():
    """Clean database before each test."""
    clear_all_todos()
    yield
    clear_all_todos()


# ============================================================================
# E2E TEST SCENARIOS
# ============================================================================

class TestUserStories:
    """Test complete user stories from start to finish."""
    
    def test_new_user_creates_first_todo(self):
        """User Story: A new user creates their first TODO item."""
        print("\n📝 Scenario: New user creates first TODO")
        
        # Step 1: Check API is accessible
        print("  1. User checks if API is available...")
        response = requests.get(f"{BASE_URL}/", timeout=REQUEST_TIMEOUT)
        assert response.status_code == 200
        print("     ✓ API is accessible")
        
        # Step 2: User creates a TODO
        print("  2. User creates a new TODO...")
        todo_data = {
            "title": "Buy groceries",
            "description": "Milk, eggs, bread",
            "priority": "high"
        }
        create_response = requests.post(
            f"{BASE_URL}/todos",
            json=todo_data,
            timeout=REQUEST_TIMEOUT
        )
        assert create_response.status_code == 201
        todo_id = create_response.json()["id"]
        print(f"     ✓ TODO created with ID: {todo_id}")
        
        # Step 3: User views the TODO
        print("  3. User views their TODO...")
        get_response = requests.get(
            f"{BASE_URL}/todos/{todo_id}",
            timeout=REQUEST_TIMEOUT
        )
        assert get_response.status_code == 200
        todo = get_response.json()
        assert todo["title"] == todo_data["title"]
        print("     ✓ TODO details are correct")
        
        # Step 4: User checks the list
        print("  4. User checks their TODO list...")
        list_response = requests.get(f"{BASE_URL}/todos", timeout=REQUEST_TIMEOUT)
        assert list_response.status_code == 200
        todos = list_response.json()
        assert len(todos) == 1
        print("     ✓ TODO appears in the list")
        print("  ✅ User story completed!\n")
    
    def test_user_manages_multiple_todos(self):
        """User Story: A user manages multiple TODO items."""
        print("\n📋 Scenario: User manages multiple TODOs")
        
        # Create 3 TODOs
        print("  1. User creates 3 TODOs...")
        todos = [
            {"title": "High priority task", "priority": "high"},
            {"title": "Medium priority task", "priority": "medium"},
            {"title": "Low priority task", "priority": "low"}
        ]
        
        created_ids = []
        for todo in todos:
            response = requests.post(
                f"{BASE_URL}/todos",
                json=todo,
                timeout=REQUEST_TIMEOUT
            )
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        print(f"     ✓ Created 3 TODOs: {created_ids}")
        
        # Update one
        print("  2. User updates first TODO...")
        response = requests.put(
            f"{BASE_URL}/todos/{created_ids[0]}",
            json={"title": "Updated task"},
            timeout=REQUEST_TIMEOUT
        )
        assert response.status_code == 200
        print("     ✓ TODO updated")
        
        # Complete one
        print("  3. User marks second TODO as completed...")
        response = requests.put(
            f"{BASE_URL}/todos/{created_ids[1]}",
            json={"completed": True},
            timeout=REQUEST_TIMEOUT
        )
        assert response.status_code == 200
        print("     ✓ TODO marked complete")
        
        # Delete one
        print("  4. User deletes third TODO...")
        response = requests.delete(
            f"{BASE_URL}/todos/{created_ids[2]}",
            timeout=REQUEST_TIMEOUT
        )
        assert response.status_code == 204
        print("     ✓ TODO deleted")
        print("  ✅ User story completed!\n")


class TestPerformance:
    """Basic performance tests."""
    
    def test_create_many_todos_quickly(self):
        """Performance Test: Creating 50 TODOs should be fast."""
        print("\n⚡ Performance Test: Creating 50 TODOs")
        
        start_time = time.time()
        for i in range(50):
            response = requests.post(
                f"{BASE_URL}/todos",
                json={"title": f"TODO {i+1}"},
                timeout=REQUEST_TIMEOUT
            )
            assert response.status_code == 201
        
        elapsed = time.time() - start_time
        print(f"  ✓ Created 50 TODOs in {elapsed:.2f}s")
        print(f"  ✓ Average: {elapsed/50*1000:.2f}ms per TODO")
        assert elapsed < 5.0
        print("  ✅ Performance acceptable!\n")


"""
HOW TO RUN:
-----------
1. Terminal 1: python todo_app.py
2. Terminal 2: pytest test_e2e.py -v -s
"""
