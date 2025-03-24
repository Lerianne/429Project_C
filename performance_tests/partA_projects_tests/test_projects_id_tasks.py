
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

#### PROJECTS/:ID/TASKS ####
def test_post_projects_id_tasks():
    project_id = create_project("Test Project for POST Tasks")

    task_data = {"title": "Test Task", "description": "Task description"}
    response = requests.post(API_URL + f"/projects/{project_id}/tasks", json=task_data)
    assert response.status_code == 201, f"POST /projects/{project_id}/tasks failed"

    # Cleanup
    delete_project(project_id)

def test_post_projects_id_tasks_fail():
    """Test creating a task under a non-existent project using POST /projects/:id/tasks (should return 404)"""
    task_data = {"title": "Orphan Task", "description": "Should fail"}
    response = requests.post(API_URL + "/projects/99999/tasks", json=task_data)
    
    assert response.status_code == 404, "Expected 404 when creating a task under a non-existent project"


def test_get_projects_id_tasks():
    project_id = create_project("Test Project for GET Tasks")

    response = requests.get(API_URL + f"/projects/{project_id}/tasks")
    assert response.status_code == 200, f"GET /projects/{project_id}/tasks failed"

    # Cleanup
    delete_project(project_id)

def test_get_projects_id_tasks_fail():
    """Test retrieving tasks from a non-existent project using GET /projects/:id/tasks (should return 404 or empty 'todos')"""
    response = requests.get(API_URL + "/projects/99999/tasks")

    # Ensure the status code is either 404 (not found) or 200 (empty tasks list)
    assert response.status_code in [200, 404], f"Unexpected response code {response.status_code}"

    if response.status_code == 200:
        response_json = response.json()

        # API should return "todos", NOT "projects"
        assert "todos" in response_json, (
            f"Expected 'todos' key in response, but got {response_json}"
        )

        # Ensure the todos list is empty
        assert response_json["todos"] == [], "Expected an empty 'todos' list for a non-existent project"

def test_head_projects_id_tasks():
    """Test HEAD request for /projects/:id/tasks"""
    project_id = create_project("Test Project for HEAD Tasks")
    
    response = requests.head(API_URL + f"/projects/{project_id}/tasks")
    assert response.status_code == 200, f"HEAD /projects/{project_id}/tasks failed"
    
    # Cleanup
    delete_project(project_id)

def test_head_projects_id_tasks_fail():
    """Test HEAD request for categories under a non-existent project"""
    response = requests.head(API_URL + "/projects/99999/tasks")
    
    # Some APIs return 200 with empty headers instead of 404
    assert response.status_code in [200, 404], f"Unexpected response code {response.status_code}"

### Testing Unsupported HTTP Methods for /projects/:id/tasks

def test_delete_projects_id_tasks():
    """Test deleting all tasks under a project using DELETE /projects/:id/tasks (should return 405)"""
    project_id = create_project("Test Project for DELETE Tasks")
    
    response = requests.delete(API_URL + f"/projects/{project_id}/tasks")
    assert response.status_code == 405, f"DELETE /projects/{project_id}/tasks should not be allowed"
    
    # Cleanup
    delete_project(project_id)

def test_delete_projects_id_tasks_fail():
    """Test deleting tasks under a non-existent project using DELETE /projects/:id/tasks (should return 405)"""
    response = requests.delete(API_URL + "/projects/99999/tasks")
    
    assert response.status_code == 405, "Expected 405 when deleting tasks under a non-existent project""Expected 404 when deleting tasks under a non-existent project"

def test_put_projects_id_tasks():
    """Test updating tasks under a project using PUT /projects/:id/tasks (should return 405)"""
    project_id = create_project("Test Project for PUT Tasks")
    
    update_data = {"title": "Updated Task Title"}
    response = requests.put(API_URL + f"/projects/{project_id}/tasks", json=update_data)
    
    assert response.status_code == 405, f"PUT /projects/{project_id}/tasks should not be allowed"
    
    # Cleanup
    delete_project(project_id)

def test_patch_projects_id_tasks():
    """Test patching tasks under a project using PATCH /projects/:id/tasks (should return 405)"""
    project_id = create_project("Test Project for PATCH Tasks")
    
    patch_data = {"title": "Patched Task Title"}
    response = requests.patch(API_URL + f"/projects/{project_id}/tasks", json=patch_data)
    
    assert response.status_code == 405, f"PATCH /projects/{project_id}/tasks should not be allowed"
    
    # Cleanup
    delete_project(project_id)

def test_options_projects_id_tasks():
    """Test OPTIONS method on /projects/:id/tasks"""
    project_id = create_project("Options Project Tasks")
    
    response = requests.options(API_URL + f"/projects/{project_id}/tasks")
    assert response.status_code == 200, f"OPTIONS /projects/{project_id}/tasks failed"
    
    # Cleanup
    delete_project(project_id)


### Summary Function to Track Tests
def test_summary(random_order = False):
    ensure_system_ready()

    test_functions = [
        test_post_projects_id_tasks,
        test_post_projects_id_tasks_fail,
        test_get_projects_id_tasks,
        test_get_projects_id_tasks_fail,
        test_head_projects_id_tasks,
        test_head_projects_id_tasks_fail,
        test_delete_projects_id_tasks,
        test_delete_projects_id_tasks_fail,
        test_options_projects_id_tasks,
        test_patch_projects_id_tasks,

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