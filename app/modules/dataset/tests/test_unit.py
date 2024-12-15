from io import BytesIO
import os
import pytest
from unittest.mock import patch
from app import create_app, db
from app.modules.dataset.models import DataSet
from app.modules.dataset.repositories import DataSetRepository
import tempfile
import shutil
from app.modules.conftest import login, logout

from app.modules.auth.models import User

from app.modules.dataset.routes import create_zip_of_datasets
from app.modules.profile.models import UserProfile


# Fixtures

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        yield app


# Fixture para simular datasets
@pytest.fixture
def mock_datasets():
    datasets = [DataSet(id=1, user_id=1), DataSet(id=2, user_id=1)]
    with patch.object(DataSetRepository, 'download_all_datasets', return_value=datasets):
        yield datasets


# Fixture para crear un usuario para login
@pytest.fixture(scope="module")
def test_client(test_client):
    """
    Extends the test_client fixture to add additional specific data for module testing.
    """
    with test_client.application.app_context():
        user_test = User(email='user@example.com', password='test1234')
        db.session.add(user_test)
        db.session.commit()

        profile = UserProfile(user_id=user_test.id, name="Name", surname="Surname")
        db.session.add(profile)
        db.session.commit()

    yield test_client


# --- Version sin loguearse ---

def test_download_all_datasets_route(app, mock_datasets):

    with app.test_client() as client:
        # Llamamos a la ruta de descarga de todos los datasets
        response = client.get("/dataset/download_all_datasets")

        # Verifica que la respuesta es exitosa
        assert response.status_code == 200
        assert "Content-Disposition" in response.headers
        assert "allDatasets.zip" in response.headers["Content-Disposition"]

    # Test para verificar que si no hay datasets se devuelve un error 404


def test_no_datasets_to_download_route(app):

    with app.test_client() as client:
        # Simulamos que no hay datasets
        with patch.object(DataSetRepository, 'download_all_datasets', return_value=[]):
            response = client.get("/dataset/download_all_datasets")

            # Verifica que la respuesta sea un 404
            assert response.status_code == 404
            assert b"No datasets found" in response.data

    # Test para verificar la gestión de excepciones al crear el zip


def test_create_zip_of_datasets_error(app, mock_datasets):

    with app.test_client() as client:
        # Simulamos una excepción al crear el ZIP
        with patch("app.modules.dataset.routes.create_zip_of_datasets", side_effect=Exception("Zip creation failed")):
            response = client.get("/dataset/download_all_datasets")

            # Verificamos que la respuesta sea un error 500
            assert response.status_code == 500
            assert b"error" in response.data


# Tests para verificar la creación y envío de un archivo ZIP

    # Test para verificar que la creación del archivo ZIP funciona

def test_create_zip_of_datasets(mock_datasets):

    # Creamos un directorio temporal
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "allDatasets.zip")

    create_zip_of_datasets(mock_datasets, zip_path)

    # Verificamos que el archivo ZIP fue creado
    assert os.path.exists(zip_path)

    shutil.rmtree(temp_dir)

    # Test para simular el envío del archivo ZIP


def test_send_zip_file(app, mock_datasets):

    with app.test_client() as client:
        # Llamamos a la ruta para crear el ZIP
        response = client.get("/dataset/download_all_datasets")

        # Verificamos que la respuesta contenga el archivo ZIP
        assert response.status_code == 200
        assert "Content-Disposition" in response.headers
        assert "allDatasets.zip" in response.headers["Content-Disposition"]

        # Verifica que el contenido del archivo no esté vacío
        zip_file = BytesIO(response.data)
        assert zip_file.getbuffer().nbytes > 0

# --- Version logueado ---

# Test para asegurar que la ruta para descargar todos los datasets funciona logueado


def test_download_all_datasets_route_with_login(test_client, mock_datasets):

    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    response = test_client.get("/dataset/download_all_datasets")
    assert response.status_code == 200
    assert "Content-Disposition" in response.headers
    assert "allDatasets.zip" in response.headers["Content-Disposition"]

    logout(test_client)

# Test para verificar que si no hay datasets se devuelve un error 404 logueado


def test_no_datasets_to_download_route_with_login(test_client):

    # Hacer login con las credenciales de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Simular que no hay datasets
    with patch.object(DataSetRepository, 'download_all_datasets', return_value=[]):
        response = test_client.get("/dataset/download_all_datasets")

        # Verificar que la respuesta sea un 404
        assert response.status_code == 404
        assert b"No datasets found" in response.data
    logout(test_client)

# Test para verificar la gestión de excepciones al crear el zip logueado


def test_create_zip_of_datasets_error_with_login(test_client, mock_datasets):

    # Hacer login con las credenciales de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Simular una excepción al crear el ZIP
    with patch("app.modules.dataset.routes.create_zip_of_datasets", side_effect=Exception("Zip creation failed")):
        response = test_client.get("/dataset/download_all_datasets")

        # Verificar que la respuesta sea un error 500
        assert response.status_code == 500
        assert b"error" in response.data
    logout(test_client)


# Test para simular el envío del archivo ZIP logueado
def test_send_zip_file_with_login(test_client, mock_datasets):

    # Hacer login con las credenciales de prueba
    login_response = login(test_client, "user@example.com", "test1234")
    assert login_response.status_code == 200, "Login was unsuccessful."

    # Llamar a la ruta para crear el ZIP
    response = test_client.get("/dataset/download_all_datasets")

    # Verificar que la respuesta contenga el archivo ZIP
    assert response.status_code == 200
    assert "Content-Disposition" in response.headers
    assert "allDatasets.zip" in response.headers["Content-Disposition"]

    # Verificar que el contenido del archivo no esté vacío
    zip_file = BytesIO(response.data)
    assert zip_file.getbuffer().nbytes > 0

    logout(test_client)


# Limpiar archivos temporales después de los tests
@pytest.fixture(scope="function", autouse=True)
def cleanup():
    temp_dir = tempfile.mkdtemp()
    yield
    shutil.rmtree(temp_dir)
