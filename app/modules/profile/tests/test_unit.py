import pytest

from app import db
from app.modules.conftest import login, logout
from app.modules.auth.models import User
from app.modules.profile.models import UserProfile


@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    for module testing (por example, new users)
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


def test_edit_profile_page_get(test_client):
    """
    Tests access to the profile editing page via a GET request.
    """
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/profile/edit")
    assert response.status_code == 200, "The profile editing page could not be accessed."
    assert b"Edit profile" in response.data, "The expected content is not present on the page"

    logout(test_client)


def test_search_user_profiles(test_client):
    """
    Test searching for user profiles by name or surname.
    """
    # Preparar la sesión de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Caso 1: Buscar un perfil existente por nombre
    response = test_client.get("/profile/search?query=Name")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"Name" in response.data, "Expected profile not found in search results by name."

    # Caso 2: Buscar un perfil existente por apellido
    response = test_client.get("/profile/search?query=Surname")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"Surname" in response.data, "Expected profile not found in search results by surname."

    # Caso 3: Buscar un término que no debería retornar resultados
    response = test_client.get("/profile/search?query=NonExistentName")
    assert response.status_code == 200, "Search request was unsuccessful."

    # Cerrar sesión después de las pruebas
    logout(test_client)


def test_search_case_insensitivity(test_client):
    """
    Test searching for user profiles by name or surname in a case-insensitive manner.
    """
    # Preparar la sesión de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Buscar por nombre con minúsculas
    response = test_client.get("/profile/search?query=name")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"Name" in response.data, "Profile not found when searching by name in lowercase."

    # Buscar por apellido con minúsculas
    response = test_client.get("/profile/search?query=surname")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"Surname" in response.data, "Profile not found when searching by surname in lowercase."

    # Buscar por nombre con mayúsculas
    response = test_client.get("/profile/search?query=NAME")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"Name" in response.data, "Profile not found when searching by name in uppercase."

    # Cerrar sesión después de las pruebas
    logout(test_client)


def test_search_empty_query(test_client):
    """
    Test searching with an empty query.
    """
    # Preparar la sesión de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Buscar con un término vacío
    response = test_client.get("/profile/search?query=")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"No profiles found" in response.data, "Unexpected profiles found when search term is empty."

    # Cerrar sesión después de las pruebas
    logout(test_client)


def test_search_single_character(test_client):
    """
    Test searching with a single character.
    """
    # Preparar la sesión de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Buscar con un término de un solo carácter
    response = test_client.get("/profile/search?query=N")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"Name" in response.data, "Expected profile not found when searching with a single character."

    # Cerrar sesión después de las pruebas
    logout(test_client)


def test_search_with_extra_spaces(test_client):
    """
    Test searching with extra spaces in the query.
    """
    # Preparar la sesión de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Buscar con espacios adicionales
    response = test_client.get("/profile/search?query=  Name  ")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"Name" in response.data, "Expected profile not found when searching with extra spaces."

    # Cerrar sesión después de las pruebas
    logout(test_client)


def test_search_no_results(test_client):
    """
    Test searching with a query that returns no results.
    """
    # Preparar la sesión de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Buscar un término que no debería devolver resultados
    response = test_client.get("/profile/search?query=NonExistentName")
    assert response.status_code == 200, "Search request was unsuccessful."
    assert b"No profiles found" in response.data, "Unexpected results when no profiles are found."

    # Cerrar sesión después de las pruebas
    logout(test_client)
