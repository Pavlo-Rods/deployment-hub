import pytest

from app.modules.dataset.models import PublicationType
from app.modules.utils.utilsdb import create_dataset_db


@pytest.fixture(scope='module')
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        # Crear datasets con combinaciones válidas y consistentes con create_dataset_db
        authors = [{"name": "Thor Odinson", "affiliation": "AI in Science", "orcid": "1111-2222"}]
        create_dataset_db(1, authors=authors, total_file_size=100000, num_files=1, tags="tag1")
        create_dataset_db(2, PublicationType.ANNOTATION_COLLECTION, tags="tag2", total_file_size=4000, num_files=2)
        create_dataset_db(3, PublicationType.BOOK, tags="tag1,tag2", date="2021-03-05", total_file_size=3000,
                          num_files=4)
        create_dataset_db(4, authors=authors, total_file_size=50000, num_files=5, tags="tag1,tag3")
        create_dataset_db(5, PublicationType.BOOK, tags="tag1,tag2", total_file_size=8000, num_files=3)
        create_dataset_db(6, PublicationType.REPORT, valid=False, tags="tag3", total_file_size=2000, num_files=1)

    yield test_client


def test_explore_get(test_client):
    response = test_client.get("/explore")
    assert response.status_code == 200, "The explore page could not be accessed."


def test_explore_post(test_client):
    search_criteria = get_search_criteria()
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    assert len(response.get_json()) == 6, "Wrong number of datasets"


def test_filter_by_publication_type(test_client):
    search_criteria = get_search_criteria(publication_type="book")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 2, f"Wrong number of datasets: {num}"

    search_criteria = get_search_criteria(publication_type="any")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets: {num}"

    search_criteria = get_search_criteria(publication_type="report")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets: {num}"

    search_criteria = get_search_criteria(publication_type="error")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets: {num}"

    search_criteria = get_search_criteria(publication_type="annotationcollection")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets: {num}"


def test_filter_by_query_string(test_client):
    search_criteria = get_search_criteria(query="Sample dataset 1")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets: {num}"

    search_criteria = get_search_criteria(query="Sample dataset 3")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets: {num}"

    dataset_not_exists = "Sample dataset wrong"
    search_criteria = get_search_criteria(query=dataset_not_exists)
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 0, f"Wrong number of datasets: {num}"


def test_sorting_mechanism(test_client):
    search_criteria = get_search_criteria(sorting="oldest")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets: {num}"


def test_filter_by_min_size(test_client):
    search_criteria = get_search_criteria(query="min_size:100")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets for min_size filter: {num}"

    search_criteria = get_search_criteria(query="min_size:50000")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 2, f"Wrong number of datasets for min_size filter: {num}"


def test_invalid_min_size_filter(test_client):
    search_criteria = get_search_criteria(query="min_size:sdw")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets for min_size filter with invalid value: {num}"

    search_criteria = get_search_criteria(query="min_size:")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets for min_size filter with empty value: {num}"


def test_invalid_max_size_filter(test_client):
    search_criteria = get_search_criteria(query="max_size:xyz")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets for max_size filter with invalid value: {num}"

    search_criteria = get_search_criteria(query="max_size:")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets for max_size filter with empty value: {num}"


def test_filter_by_max_size(test_client):
    search_criteria = get_search_criteria(query="max_size:5000")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 3, f"Wrong number of datasets for max_size filter: {num}"

    search_criteria = get_search_criteria(query="max_size:10000")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 4, f"Wrong number of datasets for max_size filter: {num}"

    search_criteria = get_search_criteria(query="max_size:100000")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 6, f"Wrong number of datasets for max_size filter: {num}"


def test_filter_by_min_models(test_client):
    search_criteria = get_search_criteria(query="models_min:2")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 4, f"Wrong number of datasets for models_min filter: {num}"

    search_criteria = get_search_criteria(query="models_min:5")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets for models_min filter: {num}"

    search_criteria = get_search_criteria(query="models_min:3")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 3, f"Wrong number of datasets for models_min filter: {num}"

    search_criteria = get_search_criteria(query="models_min:4")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 2, f"Wrong number of datasets for models_min filter: {num}"

    search_criteria = get_search_criteria(query="models_min:6")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 0, f"Wrong number of datasets for models_min filter: {num}"


def test_filter_by_max_models(test_client):
    search_criteria = get_search_criteria(query="models_max:3")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 4, f"Wrong number of datasets for models_max filter: {num}"

    search_criteria = get_search_criteria(query="models_max:4")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 5, f"Wrong number of datasets for models_max filter: {num}"

    search_criteria = get_search_criteria(query="models_max:3")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 4, f"Wrong number of datasets for models_max filter: {num}"

    search_criteria = get_search_criteria(query="models_max:2")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 3, f"Wrong number of datasets for models_max filter: {num}"

    search_criteria = get_search_criteria(query="models_max:1")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 2, f"Wrong number of datasets for models_max filter: {num}"

    search_criteria = get_search_criteria(query="models_max:0")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 0, f"Wrong number of datasets for models_max filter: {num}"


def test_filter_by_tags(test_client):
    search_criteria = get_search_criteria(query="tags:tag1")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 4, f"Wrong number of datasets for tags filter 'tag1': {num}"

    search_criteria = get_search_criteria(query="tags:tag3")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 2, f"Wrong number of datasets for tags filter 'tag3': {num}"

    search_criteria = get_search_criteria(query="tags:tag1,tag2")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 2, f"Wrong number of datasets for tags filter 'tag3': {num}"

    search_criteria = get_search_criteria(query="tags:tag1,tag3")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets for tags filter 'tag3': {num}"

    search_criteria = get_search_criteria(query="tags:tag5")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 0, f"Wrong number of datasets for tags filter 'tag3': {num}"


def test_filter_by_author(test_client):
    search_criteria = get_search_criteria(query="author:Thor Odinson")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 2, f"Wrong number of datasets for author filter: {num}"

    search_criteria = get_search_criteria(query="author:Super Mario")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 0, f"Wrong number of datasets for author filter: {num}"


def test_combined_query_filters(test_client):
    search_criteria = get_search_criteria(query="min_size:100;models_max:2;tags:tag1;author:Thor Odinson")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets for combined query filters: {num}"

    search_criteria = get_search_criteria(query="min_size:100;models_max:2;tags:tag1;author:Super Mario")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 0, f"Wrong number of datasets for combined query filters: {num}"

    search_criteria = get_search_criteria(query="max_size:5000;models_min:1;tags:tag3")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets for combined query filters: {num}"

    search_criteria = get_search_criteria(query="min_size:5000;models_min:4;tags:tag1,tag3;author:Thor Odinson")
    response = test_client.post("/explore", json=search_criteria)
    assert response.status_code == 200, "The explore page could not be accessed."
    num = len(response.get_json())
    assert num == 1, f"Wrong number of datasets for combined query filters: {num}"


def get_search_criteria(query="", sorting="newest", publication_type="any", uvl_min="", uvl_max=""):
    search_criteria = {
        "max_uvl": uvl_max,
        "min_uvl": uvl_min,
        "publication_type": publication_type,
        "query": query,
        "sorting": sorting,
    }
    return search_criteria
