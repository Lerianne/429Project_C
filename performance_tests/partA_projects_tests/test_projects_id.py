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


#### PROJECTS/:ID ####

def test_get_projects_id():
    project_id = create_project("Test Project for GET by ID")

    response = requests.get(API_URL + f"/projects/{project_id}")
    assert response.status_code == 200, f"GET /projects/{project_id} failed"

    # Cleanup
    delete_project(project_id)

def test_get_projects_id_fail():
    """Test retrieving a non-existent project (should return 404)"""
    response = requests.get(API_URL + "/projects/99999")
    assert response.status_code == 404, "Expected 404 for non-existent project"


def test_put_projects_id():
    project_id = create_project("Test Project for PUT")

    update_data = {"title": "Updated Project", "description": "Updated description"}
    response = requests.put(API_URL + f"/projects/{project_id}", json=update_data)
    assert response.status_code in [200, 204], f"PUT /projects/{project_id} failed"

    # Cleanup
    delete_project(project_id)

def test_put_projects_id_fail():
    """Test updating a non-existent project (should return 404)"""
    update_data = {"title": "Updated Nonexistent Project"}
    response = requests.put(API_URL + "/projects/99999", json=update_data)
    assert response.status_code == 404, "Expected 404 when updating a non-existent project"


def test_put_projects_id_fail():
    """Test updating a non-existent project (should return 404)"""
    update_data = {"title": "Updated Nonexistent Project"}
    response = requests.put(API_URL + "/projects/99999", json=update_data)
    assert response.status_code == 404, "Expected 404 when updating a non-existent project"

def test_post_projects_id():
    """Test modifying an existing project using POST /projects/:id"""
    project_id = create_project("Test Project for POST ID")
    
    update_data = {"title": "Modified Project Title"}
    response = requests.post(API_URL + f"/projects/{project_id}", json=update_data)
    
    assert response.status_code in [200, 204], f"POST /projects/{project_id} failed"
    
    # Verify the update
    project_response = requests.get(API_URL + f"/projects/{project_id}")
    assert project_response.json()["projects"][0]["title"] == "Modified Project Title", "Project title was not updated"
    
    # Cleanup
    delete_project(project_id)

def test_post_projects_id_fail():
    """Test modifying a non-existent project using POST /projects/:id (should return 404)"""
    update_data = {"title": "Non-existent Project"}
    response = requests.post(API_URL + "/projects/99999", json=update_data)
    
    assert response.status_code == 404, "Expected 404 when modifying a non-existent project"

def test_delete_projects_id():
    project_id = create_project("Test Project for DELETE")

    # Delete the project
    delete_project(project_id)

def test_delete_projects_id_fail():
    """Test deleting a non-existent project (should return 404)"""
    response = requests.delete(API_URL + "/projects/99999")
    assert response.status_code in [404, 204], "Expected 404 or 204 when deleting a non-existent project"

def test_head_projects_id():
    """Test HEAD request for /projects/:id"""
    project_id = create_project("Test Project for HEAD")

    response = requests.head(API_URL + f"/projects/{project_id}")
    assert response.status_code == 200, f"HEAD /projects/{project_id} failed"

    # Cleanup
    delete_project(project_id)

def test_head_projects_id_fail():
    """Test HEAD request for a non-existent project (should return 404)"""
    response = requests.head(API_URL + "/projects/99999")
    assert response.status_code == 404, "Expected 404 for HEAD on a non-existent project"


### Testing Unsupported HTTP Methods for /projects/:id

def test_patch_projects_id():
    # Create a new project
    data = {"title": "Patch Project"}
    response = requests.post(API_URL + "/projects", json=data)
    assert response.status_code == 201, "Failed to create a new project"
    project_id = response.json()["id"]

    # Attempt to PATCH the project
    update_data = {"title": "Patched Project"}
    response = requests.patch(API_URL + f"/projects/{project_id}", json=update_data)
    assert response.status_code == 405, f"PATCH /projects/{project_id} should not be allowed"

    # Cleanup
    delete_response = requests.delete(API_URL + f"/projects/{project_id}")
    assert delete_response.status_code in [200, 204], f"DELETE /projects/{project_id} failed"


def test_options_projects_id():
    # Create a new project
    data = {"title": "Options Project"}
    response = requests.post(API_URL + "/projects", json=data)
    assert response.status_code == 201, "Failed to create a new project"
    project_id = response.json()["id"]

    response = requests.options(API_URL + f"/projects/{project_id}")
    assert response.status_code == 200, f"OPTIONS /projects/{project_id} failed"

    # Cleanup
    delete_response = requests.delete(API_URL + f"/projects/{project_id}")
    assert delete_response.status_code in [200, 204], f"DELETE /projects/{project_id} failed"

# Extra tests
def test_delete_project_no_confirmation_message_allow_pass():
    try:
        # Create a new project to test deletion
        project_id = create_project("Project to Test Deletion Message Allow Pass")

        # Perform DELETE request on the created project
        response = requests.delete(API_URL + f"/projects/{project_id}")

        # Allowing the test to pass regardless of whether a confirmation message is provided
        if response.status_code in [200, 204]:
            if response.text.strip() == "":
                print("No confirmation message provided after deletion, but allowing test to pass.")
            else:
                print("Confirmation message provided after deletion.")
        else:
            assert False, f"DELETE /projects/{project_id} failed with status code {response.status_code}"

    except AssertionError as e:
        print(f"test_delete_project_no_confirmation_message_allow_pass FAILED: {e}")

def test_delete_project_no_confirmation_message():
    try:
        # Create a new project to test deletion
        project_id = create_project("Project to Test Deletion Message")

        # Perform DELETE request on the created project
        response = requests.delete(API_URL + f"/projects/{project_id}")

        # Expected behavior: The DELETE request should provide a clear confirmation message
        assert response.status_code in [200, 204], f"DELETE /projects/{project_id} failed"
        assert response.text.strip() != "", "No confirmation message provided after deletion"

    except AssertionError as e:
        print(f"test_delete_project_no_confirmation_message FAILED: {e}")
        raise e



def test_summary(random_order = False):
    ensure_system_ready()

    test_functions = [
        test_get_projects_id,
        test_get_projects_id_fail,
        test_put_projects_id,
        test_put_projects_id_fail,
        test_post_projects_id,
        test_post_projects_id_fail,
        test_delete_projects_id,
        test_delete_projects_id_fail,
        test_head_projects_id,
        test_head_projects_id_fail,
        test_patch_projects_id,
        test_options_projects_id,
        test_delete_project_no_confirmation_message,
        test_delete_project_no_confirmation_message_allow_pass,
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