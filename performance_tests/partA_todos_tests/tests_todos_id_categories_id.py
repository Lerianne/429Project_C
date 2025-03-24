import requests
import pytest
import random

BASE_URL = "http://localhost:4567/todos/1/categories/1"

# Test GET /todos/1/categories/1 failure (GET is not allowed)
def test_get_categories_1_fail():
    response = requests.get(BASE_URL)
    assert response.status_code == 404  

# Test PUT /todos/1/categories/1 failure (PUT is not allowed)
def test_put_categories_1_fail():
    response = requests.put(BASE_URL)
    assert response.status_code == 405  

# Test POST /todos/1/categories/1 failure (POST is not allowed)
def test_post_categories_1_fail():
    response = requests.post(BASE_URL)
    assert response.status_code == 404  

# Test DELETE /todos/1/categories/1 success (delete the instance of the relationship between todo and category)
def test_delete_categories_1_success():
    response = requests.delete(BASE_URL)
    assert response.status_code == 200 
    assert "categories" not in response.json() 

# Test DELETE /todos/1/categories/1 failure (trying to delete a non-existing relationship)
def test_delete_categories_1_fail():
    response = requests.delete("http://localhost:4567/todos/1/categories/1") 
    assert response.status_code == 404 

# Test OPTIONS /todos/1/categories/1 failure (OPTIONS is not allowed)
def test_options_categories_1_fail():
    response = requests.options(BASE_URL)
    assert response.status_code == 200 

# Test PATCH /todos/1/categories/1 failure (PATCH is not allowed)
def test_patch_categories_1_fail():
    response = requests.patch(BASE_URL, json={"category_id": 2})
    assert response.status_code == 405

# Test HEAD /todos/1/categories/1 failure (HEAD is not allowed)
def test_head_categories_1_fail():
    response = requests.head(BASE_URL)
    assert response.status_code == 404 

# Main function to randomize the execution of the test cases
def main():
    test_cases = [
        test_get_categories_1_fail,
        test_put_categories_1_fail,
        test_post_categories_1_fail,
        test_delete_categories_1_success,
        test_delete_categories_1_fail,
        test_options_categories_1_fail,
        test_patch_categories_1_fail,
        test_head_categories_1_fail
    ]
    
    random.shuffle(test_cases) 

    for test_case in test_cases:
        print(f"Running: {test_case.__name__}")
        test_case()

if __name__ == "__main__":
    main()
