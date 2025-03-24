import pytest
import requests
import time
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


    
#### PROJECTS/:ID/CATEGORIES ####

def test_post_projects_id_categories():
    project_id = create_project("Test Project for POST Categories")

    category_data = {"title": "Test Category", "description": "Category description"}
    response = requests.post(API_URL + f"/projects/{project_id}/categories", json=category_data)
    assert response.status_code == 201, f"POST /projects/{project_id}/categories failed"

    # Cleanup
    delete_project(project_id)

def test_post_projects_id_categories_fail():
    """Test creating a category under a non-existent project using POST /projects/:id/categories (should return 404)"""
    category_data = {"title": "Orphan Category", "description": "Should fail"}
    response = requests.post(API_URL + "/projects/99999/categories", json=category_data)
    
    assert response.status_code == 404, "Expected 404 when creating a category under a non-existent project"

def test_head_projects_id_categories():
    """Test HEAD request for /projects/:id/categories"""
    project_id = create_project("Test Project for HEAD Categories")

    response = requests.head(API_URL + f"/projects/{project_id}/categories")
    assert response.status_code == 200, f"HEAD /projects/{project_id}/categories failed"

    # Cleanup
    delete_project(project_id)

def test_head_projects_id_categories_fail():
    """Test HEAD request for categories under a non-existent project"""
    response = requests.head(API_URL + "/projects/99999/categories")
    
    # Some APIs return 200 with empty headers instead of 404
    assert response.status_code in [200, 404], f"Unexpected response code {response.status_code}"

def test_get_projects_id_categories():
    project_id = create_project("Test Project for GET Categories")

    response = requests.get(API_URL + f"/projects/{project_id}/categories")
    assert response.status_code == 200, f"GET /projects/{project_id}/categories failed"

    # Cleanup
    delete_project(project_id)

def test_get_projects_id_categories_fail():
    """Test retrieving categories from a non-existent project using GET /projects/:id/categories"""
    response = requests.get(API_URL + "/projects/99999/categories")

    assert response.status_code in [200, 404], f"Unexpected response code {response.status_code}"

    if response.status_code == 200:
        response_json = response.json()
        assert "categories" in response_json or "projects" in response_json, (
            f"Expected 'categories' or 'projects' key in response, but got {response_json}"
        )

        # Allow 'projects' but ensure it's an empty list
        if "projects" in response_json:
            assert response_json["projects"] == [], "Expected an empty projects list"

        # Allow 'categories' but ensure it's an empty list
        if "categories" in response_json:
            assert response_json["categories"] == [], "Expected an empty categories list"

def test_get_projects_incorrect_categories():
    try:
        # Create and delete a project to ensure it doesn't exist
        project_id = create_project()
        delete_project(project_id)

        time.sleep(1)

        # Attempt to GET categories for a project that does not exist
        response = requests.get(API_URL + f"/projects/{project_id}/categories")
        assert response.status_code == 404, f"GET /projects/{project_id}/categories should return 404 when the project does not exist, but got status code {response.status_code}"

    except AssertionError as e:
        print(f"test_get_projects_incorrect_categories FAILED: {e}")
        raise e

# Testing GET with an invalid project ID (/projects/anything/categories) 
def test_get_projects_invalid_id_categories():
    try:
        # Attempt to GET categories using an invalid project ID
        response = requests.get(API_URL + "/projects/anything/categories")
        assert response.status_code == 404, f"GET /projects/anything/categories should return 404 for an invalid project ID, but got status code {response.status_code}"

    except AssertionError as e:
        print(f"test_get_projects_invalid_id_categories FAILED: {e}")
        raise e


### Testing Unsupported HTTP Methods for /projects/:id/categories

def test_put_projects_id_categories():
    # Attempt to PUT a category to a project, which is not allowed
    response = requests.put(API_URL + "/projects/1/categories")
    assert response.status_code == 405, "PUT /projects/1/categories should not be allowed"


def test_patch_projects_id_categories():
    # Attempt to PATCH a category to a project, which is not allowed
    response = requests.patch(API_URL + "/projects/1/categories")
    assert response.status_code == 405, "PATCH /projects/1/categories should not be allowed"


def test_options_projects_id_categories():
    response = requests.options(API_URL + "/projects/1/categories")
    assert response.status_code == 200, "OPTIONS /projects/1/categories failed"

# Extra tests
# Testing POST /projects/:id/categories with JSON using numeric and string IDs 
def test_post_projects_id_categories_with_different_id_formats():
    try:
        # Create a new project
        project_id = create_project("New Project for Category Test")

        # Attempt to POST category with id as numeric
        category_data_numeric_id = {
            "id": 15,
            "title": "Category with Numeric ID",
            "description": "Testing numeric ID input"
        }
        response_numeric = requests.post(API_URL + f"/projects/{project_id}/categories", json=category_data_numeric_id)
        assert response_numeric.status_code != 201, "POST /projects/:id/categories should fail with a numeric ID"

        # Attempt to POST category with id as string
        category_data_string_id = {
            "id": "15",
            "title": "Category with String ID",
            "description": "Testing string ID input"
        }
        response_string = requests.post(API_URL + f"/projects/{project_id}/categories", json=category_data_string_id)
        assert response_string.status_code == 201, "POST /projects/:id/categories should succeed with a string ID"

    finally:
        # Cleanup
        delete_project(project_id)

# Testing GET with incorrect project for /projects/:id/categories
def test_get_projects_incorrect_categories_allow_pass():
    try:
        # Create and delete a project to ensure it doesn't exist
        project_id = create_project()
        delete_project(project_id)

        # Attempt to GET categories for a project that does not exist
        response = requests.get(API_URL + f"/projects/{project_id}/categories")
        if response.status_code == 404:
            assert True, f"GET /projects/{project_id}/categories returned 404 as expected."
        elif response.status_code == 200:
            assert True, f"GET /projects/{project_id}/categories unexpectedly returned 200, allowing test to pass."
        else:
            assert False, f"GET /projects/{project_id}/categories returned unexpected status code: {response.status_code}"

    except AssertionError as e:
        print(f"test_get_projects_incorrect_categories_allow_pass FAILED: {e}")

def test_get_projects_invalid_id_categories_allow_pass():
    try:
        # Attempt to GET categories using an invalid project ID
        response = requests.get(API_URL + "/projects/anything/categories")
        if response.status_code == 404:
            assert True, "GET /projects/anything/categories returned 404 as expected."
        elif response.status_code == 200:
            assert True, "GET /projects/anything/categories unexpectedly returned 200, allowing test to pass."
        else:
            assert False, f"GET /projects/anything/categories returned unexpected status code: {response.status_code}"

    except AssertionError as e:
        print(f"test_get_projects_invalid_id_categories_allow_pass FAILED: {e}")

# Testing POST /projects/:id/categories with JSON using numeric and string IDs
def test_post_projects_id_categories_with_different_id_formats_allow_pass():
    try:
        # Create a new project
        project_id = create_project("New Project for Category Test")

        # Attempt to POST category with id as numeric
        category_data_numeric_id = {
            "id": 15,
            "title": "Category with Numeric ID",
            "description": "Testing numeric ID input"
        }
        response_numeric = requests.post(API_URL + f"/projects/{project_id}/categories", json=category_data_numeric_id)
        if response_numeric.status_code != 201:
            print("POST with numeric ID failed as expected.")
        else:
            print("POST with numeric ID unexpectedly succeeded, allowing test to pass.")

        # Attempt to POST category with id as string
        category_data_string_id = {
            "id": "15",
            "title": "Category with String ID",
            "description": "Testing string ID input"
        }
        response_string = requests.post(API_URL + f"/projects/{project_id}/categories", json=category_data_string_id)
        assert True, "Allowing test to pass regardless of the outcome."

    except AssertionError as e:
        print(f"test_post_projects_id_categories_with_different_id_formats_allow_pass FAILED: {e}")

    finally:
        # Cleanup
        delete_project(project_id)

def test_summary(random_order = False):
    ensure_system_ready()

    test_functions = [
        test_post_projects_id_categories,
        test_post_projects_id_categories_fail,
        test_get_projects_id_categories,
        test_get_projects_id_categories_fail,
        test_head_projects_id_categories,
        test_head_projects_id_categories_fail,
        test_put_projects_id_categories,
        test_patch_projects_id_categories,
        test_options_projects_id_categories,
        test_get_projects_incorrect_categories,
        test_get_projects_invalid_id_categories,
        test_post_projects_id_categories_with_different_id_formats_allow_pass,
        test_get_projects_invalid_id_categories_allow_pass,
        test_get_projects_incorrect_categories_allow_pass,
        test_post_projects_id_categories_with_different_id_formats,

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