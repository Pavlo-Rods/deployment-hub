import pytest
from app.modules.conftest import login, logout
from app.modules.utils.utilsdb import create_dataset_db
from app.modules.dataset.models import PublicationType


@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Create datasets for testing
        authors = [{"name": "Thor Odinson", "affiliation": "AI in Science", "orcid": "1111-2222"}]
        create_dataset_db(1, authors=authors, total_file_size=100000, num_files=1, tags="tag1")
        create_dataset_db(2, PublicationType.ANNOTATION_COLLECTION, tags="tag2", total_file_size=4000, num_files=2)
        create_dataset_db(3, PublicationType.BOOK, tags="tag1,tag2", date="2021-03-05", total_file_size=3000,
                          num_files=4)
        create_dataset_db(4, authors=authors, total_file_size=50000, num_files=5, tags="tag1,tag3")
        create_dataset_db(5, PublicationType.BOOK, tags="tag1,tag2", total_file_size=8000, num_files=3)
        create_dataset_db(6, PublicationType.REPORT, valid=False, tags="tag3", total_file_size=2000, num_files=1)

    yield test_client


def test_user_login_and_query(test_client):
    """
    Test user login followed by a query on the explore page.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Perform a query on the explore page
    search_criteria = {
        "query": "tags:tag1",
        "sorting": "newest",
        "publication_type": "any",
    }
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    data = response.get_json()
    assert len(data) > 0, "No datasets found for the query."

    logout(test_client)


def test_user_login_and_filter_by_author(test_client):
    """
    Test user login followed by filtering datasets by author.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Filter by author
    search_criteria = {
        "query": "author:Thor Odinson",
        "sorting": "newest",
        "publication_type": "any",
    }
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    data = response.get_json()
    assert len(data) == 2, "Wrong number of datasets returned for the author filter."

    logout(test_client)


def test_user_combined_query_filters(test_client):
    """
    Test user login followed by a combined query filter.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Combined query filter
    search_criteria = {
        "query": "min_size:100;models_max:2;tags:tag1;author:Thor Odinson",
        "sorting": "newest",
        "publication_type": "any",
    }
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    data = response.get_json()
    assert len(data) == 1, "Wrong number of datasets for combined query filters."

    logout(test_client)


def test_user_invalid_query(test_client):
    """
    Test user login followed by an invalid query.
    """
    # Log in the test user
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Invalid query
    search_criteria = {
        "query": "tags:invalid_tag",
        "sorting": "newest",
        "publication_type": "any",
    }
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    data = response.get_json()
    assert len(data) == 0, "Invalid query returned results."

    logout(test_client)
