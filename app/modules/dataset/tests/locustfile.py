from io import BytesIO
from locust import HttpUser, TaskSet, task
from unittest.mock import patch
from app.modules.dataset.models import DataSet
from app.modules.dataset.repositories import DataSetRepository
from app.modules.dataset.routes import create_zip_of_datasets
import tempfile
import shutil
import os


class DatasetDownloadBehavior(TaskSet):

    @task
    def test_download_all_datasets_route(self):
        # Simula la ruta de descarga de todos los datasets
        with patch.object(DataSetRepository, 'download_all_datasets', return_value=[DataSet(id=1, user_id=1),
                                                                                    DataSet(id=2, user_id=1)]):
            response = self.client.get("/dataset/download_all_datasets")

            if response.status_code != 200:
                print(f"Download failed: {response.status_code}")
            elif "allDatasets.zip" not in response.headers.get("Content-Disposition", ""):

                print("Missing Content-Disposition header or filename")

    @task
    def test_no_datasets_to_download_route(self):
        # Simula que no hay datasets
        with patch.object(DataSetRepository, 'download_all_datasets', return_value=[]):
            response = self.client.get("/dataset/download_all_datasets")

            if response.status_code != 404:
                print(f"Expected 404, got: {response.status_code}")
            elif b"No datasets found" not in response.data:
                print("Expected error message 'No datasets found' not found in response")

    @task
    def test_create_zip_of_datasets_error(self):
        # Simula un error al crear el ZIP
        with patch("app.modules.dataset.routes.create_zip_of_datasets", side_effect=Exception("Zip creation failed")):
            response = self.client.get("/dataset/download_all_datasets")

            if response.status_code != 500:
                print(f"Expected 500 error, got: {response.status_code}")
            elif b"error" not in response.data:
                print("Expected error message not found in response")

    @task
    def test_create_zip_of_datasets(self):
        # Simula la creación de un archivo ZIP con datasets
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "allDatasets.zip")

        create_zip_of_datasets([DataSet(id=1, user_id=1), DataSet(id=2, user_id=1)], zip_path)

        if not os.path.exists(zip_path):
            print(f"Zip file not created at {zip_path}")
        shutil.rmtree(temp_dir)

    @task
    def test_send_zip_file(self):
        # Simula la descarga del archivo ZIP
        response = self.client.get("/dataset/download_all_datasets")

        if response.status_code != 200:
            print(f"Download failed: {response.status_code}")
        elif "allDatasets.zip" not in response.headers.get("Content-Disposition", ""):

            print("Missing Content-Disposition header or filename")

        # Usamos response.content en lugar de response.data
        zip_file = BytesIO(response.content)
        if zip_file.getbuffer().nbytes == 0:
            print("Downloaded ZIP file is empty")


class UserBehavior(HttpUser):
    tasks = [DatasetDownloadBehavior]
    min_wait = 5000  # Tiempo mínimo entre tareas
    max_wait = 9000  # Tiempo máximo entre tareas
    host = "http://localhost:5000"  # Reemplaza con la URL base de tu app
