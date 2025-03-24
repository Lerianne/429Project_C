import requests
import pytest
import random

BASE_URL = "http://localhost:4567/todos/1/tasksof"

# Test GET /todos/1/tasksof success (fetch all project items related to the todo by relationship "tasksof")
def test_get_tasksof_success():
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert len(response.json()) > 0 

# Test GET /todos/1/tasksof failure (when no tasks are associated with the todo)
def test_get_tasksof_fail():
    response = requests.get("http://localhost:4567/todos/-1/tasksof")
    assert response.status_code == 200  

# Test PUT /todos/1/tasksof failure (PUT is not allowed)
def test_put_tasksof_fail():
    response = requests.put(BASE_URL)

# Test POST /todos/1/tasksof failure (invalid data or missing project ID)
def test_post_tasksof_fail():
    task_data = {}  # Missing project ID
    response = requests.post(BASE_URL, json=task_data)
    assert response.status_code == 201 

# Test DELETE /todos/1/tasksof failure (DELETE is not allowed)
def test_delete_tasksof_fail():
    response = requests.delete(BASE_URL)
    assert response.status_code == 405

# Test OPTIONS /todos/1/tasksof failure (OPTIONS is not allowed)
def test_options_tasksof_fail():
    response = requests.options(BASE_URL)
    assert response.status_code == 200 

# Test PATCH /todos/1/tasksof failure (PATCH is not allowed)
def test_patch_tasksof_fail():
    response = requests.patch(BASE_URL, json={"project_id": 3})
    assert response.status_code == 405  

# Test HEAD /todos/1/tasksof success (headers for project items related to todo by tasksof relationship)
def test_head_tasksof_success():
    response = requests.head(BASE_URL)
    assert response.status_code == 200  
    assert response.headers.get("Content-Length") is None  

# Boundary Test: POST with a valid but minimal data (only project ID)
def test_post_tasksof_minimal_data():
    task_data = {"project_id": 1}  
    response = requests.post(BASE_URL, json=task_data)
    assert response.status_code == 400 

# randomize the execution of the test cases
def main():
    test_cases = [
        test_get_tasksof_success,
        test_get_tasksof_fail,
        test_put_tasksof_fail,
        test_post_tasksof_fail,
        test_delete_tasksof_fail,
        test_options_tasksof_fail,
        test_patch_tasksof_fail,
        test_head_tasksof_success,
        test_post_tasksof_minimal_data
    ]
    
    random.shuffle(test_cases) 


    for test_case in test_cases:
        print(f"Running: {test_case.__name__}")
        test_case()

if __name__ == "__main__":
    main()
