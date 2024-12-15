import pytest
from unittest.mock import patch
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        yield app


@patch("app.modules.public.routes.DataSetService")
@patch("app.modules.public.routes.FeatureModelService")
def test_dashboard_route(mock_feature_model_service, mock_dataset_service, app):
    mock_dataset_service.return_value.count_synchronized_datasets.return_value = 10
    mock_feature_model_service.return_value.count_feature_models.return_value = 5
    mock_dataset_service.return_value.total_dataset_downloads.return_value = 100
    mock_feature_model_service.return_value.total_feature_model_downloads.return_value = 50
    mock_dataset_service.return_value.total_dataset_views.return_value = 200
    mock_feature_model_service.return_value.total_feature_model_views.return_value = 150

    with app.test_client() as client:
        response = client.get("/dashboard")

        assert response.status_code == 200

        assert b"Cantidad de Datasets y Feature Models" in response.data
        assert b"Total de Descargas" in response.data
        assert b"Total de Vistas" in response.data

        assert b"10" in response.data
        assert b"5" in response.data
        assert b"100" in response.data
        assert b"200" in response.data


@patch("app.modules.public.routes.DataSetService")
@patch("app.modules.public.routes.FeatureModelService")
def test_dashboard_route_empty_values(mock_feature_model_service, mock_dataset_service, app):
    mock_dataset_service.return_value.count_synchronized_datasets.return_value = None
    mock_feature_model_service.return_value.count_feature_models.return_value = None
    mock_dataset_service.return_value.total_dataset_downloads.return_value = None
    mock_feature_model_service.return_value.total_feature_model_downloads.return_value = None
    mock_dataset_service.return_value.total_dataset_views.return_value = None
    mock_feature_model_service.return_value.total_feature_model_views.return_value = None

    with app.test_client() as client:
        response = client.get("/dashboard")

        assert response.status_code == 200

        assert b"Cantidad de Datasets y Feature Models" in response.data
        assert b"Total de Descargas" in response.data
        assert b"Total de Vistas" in response.data

        assert b"0" in response.data


@patch("app.modules.public.routes.DataSetService")
@patch("app.modules.public.routes.FeatureModelService")
def test_dashboard_route_service_error(mock_feature_model_service, mock_dataset_service, app):
    mock_dataset_service.side_effect = Exception("Error al obtener datasets")
    mock_feature_model_service.return_value.count_feature_models.return_value = 5
    mock_dataset_service.return_value.total_dataset_downloads.return_value = 100
    mock_feature_model_service.return_value.total_feature_model_downloads.return_value = 50
    mock_dataset_service.return_value.total_dataset_views.return_value = 200
    mock_feature_model_service.return_value.total_feature_model_views.return_value = 150

    with app.test_client() as client:
        response = client.get("/dashboard")

        assert response.status_code == 500

        assert b"Error al obtener datasets" in response.data


@patch("app.modules.public.routes.DataSetService")
@patch("app.modules.public.routes.FeatureModelService")
def test_dashboard_route_large_values(mock_feature_model_service, mock_dataset_service, app):
    mock_dataset_service.return_value.count_synchronized_datasets.return_value = 1000000
    mock_feature_model_service.return_value.count_feature_models.return_value = 500000
    mock_dataset_service.return_value.total_dataset_downloads.return_value = 10000000
    mock_feature_model_service.return_value.total_feature_model_downloads.return_value = 5000000
    mock_dataset_service.return_value.total_dataset_views.return_value = 20000000
    mock_feature_model_service.return_value.total_feature_model_views.return_value = 15000000

    with app.test_client() as client:
        response = client.get("/dashboard")

        assert response.status_code == 200

        assert b"1000000" in response.data
        assert b"500000" in response.data
        assert b"10000000" in response.data
        assert b"20000000" in response.data
