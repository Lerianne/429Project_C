import requests
import pytest
import random

BASE_URL = "http://localhost:4567/todos/1/categories"

# Test GET /todos/1/categories success (fetch all category items related to the todo by relationship "categories")
def test_get_categories_success():
    response = requests.get(BASE_URL)
    assert response.status_code == 200
    assert isinstance(response.json().get("categories"), list)

# Test PUT /todos/1/categories failure (PUT is not allowed)
def test_put_categories_fail():
    response = requests.put(BASE_URL)
    assert response.status_code == 405  

# Test POST /todos/1/categories failure (invalid data or missing category ID)
def test_post_categories_fail():
    category_data = {}  
    response = requests.post(BASE_URL, json=category_data)
    assert response.status_code == 400  

# Test DELETE /todos/1/categories failure (DELETE is not allowed)
def test_delete_categories_fail():
    response = requests.delete(BASE_URL)
    assert response.status_code == 405 

# Test OPTIONS /todos/1/categories failure (OPTIONS is not allowed)
def test_options_categories_fail():
    response = requests.options(BASE_URL)
    assert response.status_code == 200 

# Test PATCH /todos/1/categories failure (PATCH is not allowed)
def test_patch_categories_fail():
    response = requests.patch(BASE_URL, json={"category_id": 3})  
    assert response.status_code == 405  

# Test HEAD /todos/1/categories success (headers for category items related to todo by categories relationship)
def test_head_categories_success():
    response = requests.head(BASE_URL)
    assert response.status_code == 200
    assert response.headers.get("Transfer-Encoding") == "chunked"

# Test HEAD /todos/1/categories failure (wrong todo ID)
def test_head_categories_fail():
    response = requests.head("http://localhost:4567/todos/999/categories") 
    assert response.status_code == 200  

# Boundary Test: POST with a valid but minimal data (only category ID)
def test_post_categories_minimal_data():
    category_data = {"category_id": 1}  
    response = requests.post(BASE_URL, json=category_data)
    assert response.status_code == 400 

# Boundary Test: POST with maximum data (check large category ID or other constraints)
def test_post_categories_maximum_data():
    category_data = {"category_id": 999999999}
    response = requests.post(BASE_URL, json=category_data)
    assert response.status_code == 400
    assert "errorMessages" in response.json()

# Main function to randomize the execution of the test cases
def main():
    test_cases = [
        test_get_categories_success,
        test_put_categories_fail,
        test_post_categories_fail,
        test_delete_categories_fail,
        test_options_categories_fail,
        test_patch_categories_fail,
        test_head_categories_success,
        test_head_categories_fail,
        test_post_categories_minimal_data,
        test_post_categories_maximum_data
    ]
    
    random.shuffle(test_cases)  

    for test_case in test_cases:
        print(f"Running: {test_case.__name__}")
        test_case()

if __name__ == "__main__":
    main()
