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


#### PROJECTS ####
def test_get_projects():
    project_id = create_project("Test Project for GET")

    response = requests.get(API_URL + "/projects")
    assert response.status_code == 200, "GET /projects failed"

    # Cleanup
    delete_project(project_id)

def test_get_projects_fail():
    """Test GET /projects when no projects exist (should return an empty list)"""
    
    # Get all projects
    response = requests.get(API_URL + "/projects")
    if response.status_code == 200 and "projects" in response.json():
        # Delete all projects one by one
        for project in response.json()["projects"]:
            requests.delete(f"{API_URL}/projects/{project['id']}")

    # Now reattempt GET request
    response = requests.get(API_URL + "/projects")
    
    # Expecting 200 with an empty list
    assert response.status_code == 200, "Expected 200 even if no projects exist"
    assert response.json() == {"projects": []}, f"Expected an empty projects list, but got {response.json()}"


def test_post_projects():
    project_id = create_project("Test Project for POST")

    # Verify the project creation
    response = requests.get(API_URL + f"/projects/{project_id}")
    assert response.status_code == 200, f"GET /projects/{project_id} failed"

    # Cleanup
    delete_project(project_id)

def test_post_projects_fail():
    """Test POST /projects with missing required fields. API unexpectedly allows this, so verify behavior."""

    # Sending an empty JSON body
    payload = {}
    response = requests.post(API_URL + "/projects", json=payload)

    # The API allows this (expected 400, but it gives 201)
    assert response.status_code in [201, 400], (
    f"Unexpected response: {response.status_code}, response body: {response.json()}")

    # If a project was created, retrieve it and check if it has an ID
    project_id = response.json().get("id")
    assert project_id, "API created a project, but no ID was returned"

    # Fetch the project details
    project_response = requests.get(API_URL + f"/projects/{project_id}")
    project_data = project_response.json()

    # Since the API allows creation, check if it at least assigned an ID
    assert "projects" in project_data, "Expected 'projects' key in response"
    assert len(project_data["projects"]) > 0, "Expected at least one project"

    # Cleanup: Delete the newly created project
    delete_response = requests.delete(API_URL + f"/projects/{project_id}")
    assert delete_response.status_code in [200, 204], f"Failed to delete test project {project_id}"


def test_head_projects():
    project_id = create_project("Test Project for HEAD")

    response = requests.head(API_URL + "/projects")
    assert response.status_code == 200, "HEAD /projects failed"

    # Cleanup
    delete_project(project_id)

def test_head_projects_fail():
    """Test HEAD /projects when no projects exist (should still return 200)"""
    # Ensure no projects exist
    requests.delete(API_URL + "/projects")

    response = requests.head(API_URL + "/projects")
    
    # Expecting 200, even if no data exists (HEAD should return only headers)
    assert response.status_code == 200, "HEAD /projects should return 200 even if empty"
    assert "Content-Type" in response.headers, "Expected headers in response"


### Testing Unsupported HTTP Methods for /projects


def test_delete_projects():
    response = requests.delete(API_URL + "/projects")
    assert response.status_code == 405, "DELETE /projects should not be allowed"


def test_patch_projects():
    data = {"title": "Patch Project"}
    response = requests.patch(API_URL + "/projects", json=data)
    assert response.status_code == 405, "PATCH /projects should not be allowed"


def test_options_projects():
    response = requests.options(API_URL + "/projects")
    assert response.status_code == 200, "OPTIONS /projects failed"




def test_summary(random_order=False):
    ensure_system_ready()

    test_functions = [
        test_get_projects,
        test_get_projects_fail,
        test_post_projects,
        test_post_projects_fail,
        test_head_projects,
        test_head_projects_fail,
        test_delete_projects,
        test_patch_projects,
        test_options_projects,
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