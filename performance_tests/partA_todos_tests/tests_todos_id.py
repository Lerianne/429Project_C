import requests
import random
import pytest

BASE_URL = "http://localhost:4567/todos/1"

# Test GET /todos/1 success (fetch a specific todo by ID)
def test_get_todo_by_id_success():
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert "todos" in response.json()
    assert len(response.json()['todos']) > 0  

# Test GET /todos/1 failure (invalid ID or non-existing todo)
def test_get_todo_by_id_fail():
    response = requests.get("http://localhost:4567/todos/999")
    assert response.status_code == 404 

# Test POST /todos/1/tasksof success (post data to a specific todo, here assuming it's to associate 'tasksof')
def test_post_tasksof_success():
    task_data = {"project_id": 2}  # Assuming we're associating with project 2
    response = requests.post(f"{BASE_URL}/tasksof", json=task_data)
    assert response.status_code == 201 
    print(response.json())

# Test POST /todos/1/tasksof failure (incorrect data type for tasksof association)
def test_post_tasksof_fail():
    task_data = "invalid_data_type"  
    response = requests.post(f"{BASE_URL}/tasksof", json=task_data)
    assert response.status_code == 400 

# Test GET /todos/1/tasksof success (fetch tasksof for specific todo)
def test_get_tasksof_success():
    response = requests.get(f"{BASE_URL}/tasksof")
    assert response.status_code == 200
    assert "projects" in response.json()
    assert isinstance(response.json()['projects'], list)  
    print(response.json())  

# Test GET /todos/999/tasksof failure (non-existing todo tasksof with different error response)
def test_get_tasksof_fail():
    response = requests.get("http://localhost:4567/todos/999/tasksof")
    assert response.status_code == 404
    assert "error" in response.json() 

# Test PUT /todos/1/tasksof failure (incorrect tasksof data for updating)
def test_put_tasksof_fail():
    updated_task = {}  # Missing necessary project_id
    response = requests.put(f"{BASE_URL}/tasksof", json=updated_task)
    assert response.status_code == 405 

# Test DELETE /todos/1/tasksof failure (delete not allowed on tasksof)
def test_delete_tasksof_fail():
    response = requests.delete(f"{BASE_URL}/tasksof")
    assert response.status_code == 405 

# Test OPTIONS /todos/1/tasksof failure (OPTIONS not supported)
def test_options_tasksof_fail():
    response = requests.options(f"{BASE_URL}/tasksof")
    assert response.status_code == 200 

# Main function to randomize the execution of the test cases
def main():
    test_cases = [
        test_get_todo_by_id_success,
        test_get_todo_by_id_fail,
        test_post_tasksof_success,
        test_post_tasksof_fail,
        test_get_tasksof_success,
        test_get_tasksof_fail,
        test_put_tasksof_fail,
        test_delete_tasksof_fail,
        test_options_tasksof_fail
    ]
    
    random.shuffle(test_cases)  


    for test_case in test_cases:
        print(f"Running: {test_case.__name__}")
        test_case()

if __name__ == "__main__":
    main()
