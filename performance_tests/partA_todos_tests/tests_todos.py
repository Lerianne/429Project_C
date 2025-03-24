import requests
import pytest
import random
import sys

BASE_URL = "http://localhost:4567/todos"


# Test GET /todos failure (when it doesn't exist or connection issues)
def test_get_todos_fail():
    response = requests.get(f"{BASE_URL}?invalid_param=test")
    assert response.status_code == 200 

# Test PUT /todos (not allowed)
def test_put_todos_fail():
    response = requests.put(BASE_URL, json={"title": "Test Todo"})
    assert response.status_code == 405  

# Test POST /todos success (create a new todo without ID)
def test_post_todos_success():
    new_todo = {"title": "New Todo", "description": "Description of new todo"}
    response = requests.post(BASE_URL, json=new_todo)
    assert response.status_code == 201 
    response_json = response.json()
    assert "id" in response_json

# Test POST /todos failure (missing required fields like title)
def test_post_todos_fail():
    new_todo = {"description": "Missing title"}
    response = requests.post(BASE_URL, json=new_todo)
    assert response.status_code == 400  
    assert "title" in response.text 

# Test DELETE /todos (not allowed)
def test_delete_todos_fail():
    response = requests.delete(BASE_URL, json={"id": 1})
    assert response.status_code == 405  

# Test OPTIONS /todos (not allowed)
def test_options_todos_fail():
    response = requests.options(BASE_URL)
    assert response.status_code == 200  

# Test PATCH /todos (not allowed)
def test_patch_todos_fail():
    response = requests.patch(BASE_URL, json={"id": 1, "title": "Updated Todo"})
    assert response.status_code == 405 

# Test HEAD /todos success (Check existence of todos)
def test_head_todos_success():
    response = requests.head(BASE_URL)
    assert response.status_code == 200
    assert "Transfer-Encoding" in response.headers

# Test HEAD /todos failure (when no todos available or incorrect URL)
def test_head_todos_fail():
    response = requests.head(f"{BASE_URL}?invalid_param=test")
    assert response.status_code == 200  

# Boundary Test: Creating a Todo with minimum data (only title)
def test_post_todos_minimum_data():
    new_todo = {"title": "Minimal Todo"}
    response = requests.post(BASE_URL, json=new_todo)
    assert response.status_code == 201
    response_json = response.json()
    assert "id" in response_json

# Boundary Test: Creating a Todo with maximum allowed fields (testing length or other constraints)
def test_post_todos_maximum_data():
    new_todo = {
        "title": "A" * 255, 
        "description": "B" * 1000,  
    }
    response = requests.post(BASE_URL, json=new_todo)
    assert response.status_code == 201
    response_json = response.json()
    assert "id" in response_json

# Test GET /todos with specific query (for filtering)
def test_get_todos_with_query():
    response = requests.get(f"{BASE_URL}?title=Test Todo")
    assert response.status_code == 200
    todos = response.json().get('todos', [])
    assert all(todo['title'] == 'Test Todo' for todo in todos)

# Function to run tests with optional randomization
def run_tests(randomize=False):
    test_functions = [
        test_get_todos_fail,
        test_put_todos_fail,
        test_post_todos_success,
        test_post_todos_fail,
        test_delete_todos_fail,
        test_options_todos_fail,
        test_patch_todos_fail,
        test_head_todos_success,
        test_head_todos_fail,
        test_post_todos_minimum_data,
        test_post_todos_maximum_data,
        test_get_todos_with_query,
    ]

    if randomize:
        random.shuffle(test_functions)
    for test in test_functions:
        try:
            test()
            print(f"Test {test.__name__}: PASSED")
        except AssertionError as e:
            print(f"Test {test.__name__}: FAILED - {e}")

if __name__ == "__main__":
    randomize_tests = "--random" in sys.argv
    run_tests(randomize=randomize_tests)
