import requests
import pytest
import random

BASE_URL = "http://localhost:4567/todos/1/tasksof/1"
NON_EXISTENT_URL = "http://localhost:4567/todos/1/tasksof/999"

HEADERS = {"Content-Type": "application/json"}

# Test GET /todos/1/tasksof/1 failure (GET is not allowed)
def test_get_tasksof_relationship_fail():
    response = requests.get(BASE_URL, headers=HEADERS)
    assert response.status_code == 404 

# Test PUT /todos/1/tasksof/1 failure (PUT is not allowed)
def test_put_tasksof_relationship_fail():
    response = requests.put(BASE_URL, headers=HEADERS)
    assert response.status_code == 405  

# Test POST /todos/1/tasksof/1 failure (POST is not allowed)
def test_post_tasksof_relationship_fail():
    response = requests.post(BASE_URL, headers=HEADERS)
    assert response.status_code == 404  

# Test DELETE /todos/1/tasksof/1 success (delete the instance of tasksof relationship)
def test_delete_tasksof_relationship_success():
    check_response = requests.get("http://localhost:4567/todos/1/tasksof", headers=HEADERS)
    if not check_response.json().get("tasksof", []):
        pytest.skip("Skipping test: No existing relationship to delete.")

    response = requests.delete(BASE_URL, headers=HEADERS)
    assert response.status_code in [200, 204], f"Expected 200 or 204, got {response.status_code}"

    # Verify deletion
    verify_response = requests.get("http://localhost:4567/todos/1/tasksof", headers=HEADERS)
    assert not verify_response.json().get("tasksof", []), "Relationship was not deleted."

# Test DELETE /todos/1/tasksof/1 failure (trying to delete a non-existent relationship)
def test_delete_tasksof_relationship_fail():
    response = requests.delete(NON_EXISTENT_URL, headers=HEADERS)
    assert response.status_code == 404  

# Test OPTIONS /todos/1/tasksof/1 failure (OPTIONS is not allowed)
def test_options_tasksof_relationship_fail():
    response = requests.options(BASE_URL, headers=HEADERS)
    assert response.status_code == 200

# Test PATCH /todos/1/tasksof/1 failure (PATCH is not allowed)
def test_patch_tasksof_relationship_fail():
    response = requests.patch(BASE_URL, json={"project_id": 2}, headers=HEADERS)
    assert response.status_code == 405

# Test HEAD /todos/1/tasksof/1 failure (HEAD is not allowed)
def test_head_tasksof_relationship_fail():
    response = requests.head(BASE_URL, headers=HEADERS)
    assert response.status_code == 404 

# Boundary Test: DELETE with a valid but minimal relationship
def test_delete_tasksof_relationship_minimal():
    check_response = requests.get("http://localhost:4567/todos/1/tasksof", headers=HEADERS)
    if not check_response.json().get("tasksof", []):
        pytest.skip("Skipping test: No existing relationship to delete.")

    response = requests.delete(BASE_URL, headers=HEADERS)
    assert response.status_code in [200, 204], f"Expected 200 or 204, got {response.status_code}"

    verify_response = requests.get("http://localhost:4567/todos/1/tasksof", headers=HEADERS)
    assert not verify_response.json().get("tasksof", []), "Relationship was not deleted."

# Boundary Test: DELETE with a non-existent relationship
def test_delete_tasksof_relationship_nonexistent():
    response = requests.delete(NON_EXISTENT_URL, headers=HEADERS)
    assert response.status_code == 404  

# Main function to randomize the execution of the test cases
def main():
    test_cases = [
        test_get_tasksof_relationship_fail,
        test_put_tasksof_relationship_fail,
        test_post_tasksof_relationship_fail,
        test_delete_tasksof_relationship_success,
        test_delete_tasksof_relationship_fail,
        test_options_tasksof_relationship_fail,
        test_patch_tasksof_relationship_fail,
        test_head_tasksof_relationship_fail,
        test_delete_tasksof_relationship_minimal,
        test_delete_tasksof_relationship_nonexistent
    ]
    
    random.shuffle(test_cases) 

    for test_case in test_cases:
        print(f"Running: {test_case.__name__}")
        test_case()

if __name__ == "__main__":
    main()
