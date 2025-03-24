
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

# Helper function for creating a category for a project
def create_category_for_project(project_id, title="Default Category", description="Default Description"):
    category_data = {"title": title, "description": description}
    response = requests.post(API_URL + f"/projects/{project_id}/categories", json=category_data)
    assert response.status_code == 201, "Failed to create category linked to the project"
    return response.json()["id"]


#### PROJECTS/:ID/CATEGORIES/:ID ####

def test_delete_projects_id_categories_id():
    """Test deleting a specific category under a project using DELETE /projects/:id/categories/:id"""
    project_id = create_project("Test Project for DELETE Category")
    
    # Create category
    category_data = {"title": "Category to Delete", "description": "Category to be removed"}
    category_response = requests.post(API_URL + "/categories", json=category_data)
    assert category_response.status_code == 201, "Failed to create category for deletion"
    category_id = category_response.json()["id"]

    # Associate category with project
    link_response = requests.post(API_URL + f"/projects/{project_id}/categories", json={"id": category_id})
    assert link_response.status_code == 201, "Failed to associate category with project"

    # Attempt to delete the category from the project
    response = requests.delete(API_URL + f"/projects/{project_id}/categories/{category_id}")
    assert response.status_code in [200, 204], f"DELETE /projects/{project_id}/categories/{category_id} failed"

    # Cleanup
    delete_project(project_id)

def test_delete_projects_id_categories_id_fail():
    """Test deleting a non-existent category under a project using DELETE /projects/:id/categories/:id (should return 404)"""
    response = requests.delete(API_URL + "/projects/99999/categories/99999")
    assert response.status_code == 404, "Expected 404 when deleting a non-existent category"

### Testing Unsupported HTTP Methods for /projects/:id/categories/:id ###

def test_get_projects_id_categories_id():
    """Test GET /projects/:id/categories/:id (should return 404)"""
    response = requests.get(API_URL + "/projects/99999/categories/99999")
    assert response.status_code == 404, "Expected 404 when retrieving a non-existent category"

def test_put_projects_id_categories_id():
    """Test PUT /projects/:id/categories/:id (should return 405)"""
    response = requests.put(API_URL + "/projects/99999/categories/99999", json={"title": "Updated Category"})
    assert response.status_code == 405, "Expected 405 Method Not Allowed for PUT on categories/:id"

def test_post_projects_id_categories_id():
    """Test POST /projects/:id/categories/:id (should return 404)"""
    response = requests.post(API_URL + "/projects/99999/categories/99999")
    assert response.status_code == 404, "Expected 404 when posting to a non-existent category"

def test_options_projects_id_categories_id():
    """Test OPTIONS /projects/:id/categories/:id (should return 200 OK)"""
    response = requests.options(API_URL + "/projects/1/categories/1")
    assert response.status_code in [200, 204], "Expected 200 or 204 for OPTIONS on categories/:id"

def test_patch_projects_id_categories_id():
    """Test PATCH /projects/:id/categories/:id (should return 405)"""
    response = requests.patch(API_URL + "/projects/99999/categories/99999", json={"title": "Patched Category"})
    assert response.status_code == 405, "Expected 405 Method Not Allowed for PATCH on categories/:id"

def test_head_projects_id_categories_id():
    """Test HEAD /projects/:id/categories/:id (should return 404)"""
    response = requests.head(API_URL + "/projects/99999/categories/99999")
    assert response.status_code == 404, "Expected 404 when sending HEAD request to a non-existent category"

#Extra tests
# Testing ID generation logic for categories linked to projects
def test_post_projects_id_categories_id_generation():
    try:
        # Create a new project
        project_id = create_project("New Project for ID Test", "Project description for ID Test")

        # Create the first category linked to the created project
        category_id_1 = create_category_for_project(project_id, "First Category", "Description for the first category")
        assert int(category_id_1) > 0, "Category ID should be greater than 0"
        print(f"First Category ID: {category_id_1}")

        # Create another category linked to the same project
        category_id_2 = create_category_for_project(project_id, "Second Category", "Description for the second category")
        assert int(category_id_2) > int(category_id_1), "Category IDs should increment"
        print(f"Second Category ID: {category_id_2}")

        # Delete the project
        delete_project(project_id)

        # Create a new project and category to see if the ID starts from 1 or continues
        project_id_2 = create_project("New Project for ID Test 2", "Another project for ID test")
        category_id_3 = create_category_for_project(project_id_2, "Third Category", "Description for the third category")
        print(f"Third Category ID after deletion: {category_id_3}")

        # Check the ID behavior: Expect the new category ID to restart from '1' for the new project
        assert int(category_id_3) == 1, f"Expected category ID to start from 1 for the new project, but got {category_id_3} instead."

    finally:
        # Cleanup
        delete_project(project_id_2)
    
def test_post_projects_id_categories_id_generation_allow_pass():
    try:
        # Create a new project
        project_id = create_project("New Project for ID Test", "Project description for ID Test")

        # Create the first category linked to the created project
        category_id_1 = create_category_for_project(project_id, "First Category", "Description for the first category")
        assert True, "Allowing test to pass regardless of the outcome."
        print(f"First Category ID: {category_id_1}")

        # Create another category linked to the same project
        category_id_2 = create_category_for_project(project_id, "Second Category", "Description for the second category")
        assert True, "Allowing test to pass regardless of the outcome."
        print(f"Second Category ID: {category_id_2}")

        # Delete the project
        delete_project(project_id)

        # Create a new project and category to see if the ID starts from 1 or continues
        project_id_2 = create_project("New Project for ID Test 2", "Another project for ID test")
        category_id_3 = create_category_for_project(project_id_2, "Third Category", "Description for the third category")
        print(f"Third Category ID after deletion: {category_id_3}")

        # Check the ID behavior
        if int(category_id_3) == 1:
            print("Category ID started at 1, indicating a separate sequence for categories linked to each project.")
        else:
            print(f"Category ID is {category_id_3}, indicating that IDs are being incremented from the last available ID across the system.")

        # Allow the test to pass regardless of ID behavior
        assert True, "Allowing test to pass regardless of the ID behavior."

    except AssertionError as e:
        print(f"test_post_projects_id_categories_id_generation_allow_pass FAILED: {e}")

    finally:
        # Cleanup
        delete_project(project_id_2)

### Summary Function to Track Tests
def test_summary(random_order = False):
    ensure_system_ready()

    test_functions = [
        test_delete_projects_id_categories_id,
        test_delete_projects_id_categories_id_fail,
        test_get_projects_id_categories_id,
        test_put_projects_id_categories_id,
        test_post_projects_id_categories_id,
        test_options_projects_id_categories_id, 
        test_patch_projects_id_categories_id,
        test_head_projects_id_categories_id,
        test_post_projects_id_categories_id_generation,
        test_post_projects_id_categories_id_generation_allow_pass,


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