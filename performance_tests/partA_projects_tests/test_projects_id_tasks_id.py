

import pytest
import requests
import random
import sys

API_URL = "http://localhost:4567"

# Documented Capabilities Tests

def ensure_system_ready():
    try:
        response = requests.get(API_URL)
        assert response.status_code == 200, "API is not active"
    except requests.exceptions.ConnectionError:
        raise AssertionError("API is not active or could not connect")

# Create a project
def create_project(title="Default Project", description="Default Description"):
    data = {"title": title, "description": description}
    response = requests.post(API_URL + "/projects", json=data)
    assert response.status_code == 201, "Failed to create project"
    return response.json()["id"]

# delete a project
def delete_project(project_id):
    response = requests.delete(API_URL + f"/projects/{project_id}")
    assert response.status_code in [200, 204], f"DELETE /projects/{project_id} failed"



#### PROJECTS/:ID/TASKS/:ID ####

def test_delete_projects_id_tasks_id():
    """Test deleting a specific task under a project using DELETE /projects/:id/tasks/:id"""
    project_id = create_project("Test Project for DELETE Task")
    task_data = {"title": "Task to Delete", "description": "Task to be removed"}
    task_response = requests.post(API_URL + f"/projects/{project_id}/tasks", json=task_data)
    assert task_response.status_code == 201, "Failed to create task for deletion"
    task_id = task_response.json()["id"]
    
    response = requests.delete(API_URL + f"/projects/{project_id}/tasks/{task_id}")
    assert response.status_code in [200, 204], f"DELETE /projects/{project_id}/tasks/{task_id} failed"
    
    # Cleanup
    delete_project(project_id)

def test_delete_projects_id_tasks_id_fail():
    """Test deleting a non-existent task under a project using DELETE /projects/:id/tasks/:id (should return 404)"""
    response = requests.delete(API_URL + "/projects/99999/tasks/99999")
    assert response.status_code == 404, "Expected 404 when deleting a non-existent task"

### Testing Unsupported HTTP Methods for /projects/:id/tasks/:id ###

def test_get_projects_id_tasks_id():
    """Test GET /projects/:id/tasks/:id (should return 404)"""
    response = requests.get(API_URL + "/projects/99999/tasks/99999")
    assert response.status_code == 404, "Expected 404 when retrieving a non-existent task"

def test_put_projects_id_tasks_id():
    """Test PUT /projects/:id/tasks/:id (should return 405)"""
    response = requests.put(API_URL + "/projects/99999/tasks/99999", json={"title": "Updated Task"})
    assert response.status_code == 405, "Expected 405 Method Not Allowed for PUT on tasks/:id"

def test_post_projects_id_tasks_id():
    """Test POST /projects/:id/tasks/:id (should return 404)"""
    response = requests.post(API_URL + "/projects/99999/tasks/99999")
    assert response.status_code == 404, "Expected 404 when posting to a non-existent task"

def test_options_projects_id_tasks_id():
    """Test OPTIONS /projects/:id/tasks/:id (should return 200 OK)"""
    response = requests.options(API_URL + "/projects/1/tasks/1")
    assert response.status_code in [200, 204], "Expected 200 or 204 for OPTIONS on tasks/:id"

def test_patch_projects_id_tasks_id():
    """Test PATCH /projects/:id/tasks/:id (should return 405)"""
    response = requests.patch(API_URL + "/projects/99999/tasks/99999", json={"title": "Patched Task"})
    assert response.status_code == 405, "Expected 405 Method Not Allowed for PATCH on tasks/:id"

def test_head_projects_id_tasks_id():
    """Test HEAD /projects/:id/tasks/:id (should return 404)"""
    response = requests.head(API_URL + "/projects/99999/tasks/99999")
    assert response.status_code == 404, "Expected 404 when sending HEAD request to a non-existent task"

### Summary Function to Track Tests
def test_summary(random_order = False):
    ensure_system_ready()

    test_functions = [
        test_delete_projects_id_tasks_id,
        test_delete_projects_id_tasks_id_fail,
        test_get_projects_id_tasks_id,
        test_put_projects_id_tasks_id,
        test_post_projects_id_tasks_id,
        test_options_projects_id_tasks_id, 
        test_patch_projects_id_tasks_id,
        test_head_projects_id_tasks_id,

    ]
    if random_order:
        random.seed(42)  # Set a fixed seed for reproducibility
        random.shuffle(test_functions)

    passed_tests = 0
    failed_tests = 0

    print("\nExecuting tests" + (" in random order" if random_order else " in default order") + ":\n")
   
    for test in test_functions:
        try:
            test()
            print(f"Test {test.__name__}: PASSED")
            passed_tests += 1
        except AssertionError as e:
            print(f"Test {test.__name__}: FAILED - {e}")
            failed_tests += 1

    print("\nSummary:")
    print(f"Total tests run: {len(test_functions)}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")


# Running all the tests
if __name__ == "__main__":
    try:
        ensure_system_ready()
        run_tests = True
    except AssertionError as e:
        print(f"System not ready: {e}")
        run_tests = False

    if run_tests:
        # Check if --random was provided as a command-line argument
        random_mode = "--random" in sys.argv
        test_summary(random_mode)

    # Run tests using pytest
    if run_tests:
        pytest_args = ["-s"]
        if random_mode:
            pytest_args.extend(["--random-order", "--randomly-seed=42"])

        pytest.main([__file__, *pytest_args])

        response = requests.get(API_URL)
        assert response.status_code == 200, "API is already shutdown"
        try:
            response = requests.get(API_URL + "/shutdown")
        except requests.exceptions.ConnectionError:
            assert True
    else:
        print("Tests skipped: API is not running or could not be reached.")