import logging
import os

from dotenv import load_dotenv
from flask_login import current_user

from app.modules.dataset.models import DSMetaData, DataSet
from app.modules.fakenodo.models import Deposition
from app.modules.fakenodo.repositories import DepositionRepository
from app.modules.featuremodel.models import FeatureModel

from core.configuration.configuration import uploads_folder_name
from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)

load_dotenv()


class DepositionService(BaseService):
    def __init__(self):
        self.deposition_repository = DepositionRepository()

    # Metodos Principales

    def createDeposition(self, dataset: DataSet, doi: str = None) -> dict:

        deposition_id = dataset.id
        deposition_metadata = self._buildMetadata(dataset)

        if doi:
            deposition_doi = f"{doi}/UVL{deposition_id}"
        else:
            deposition_doi = None

        try:
            deposition = self.deposition_repository.createDeposition(metadata=deposition_metadata)

            res = {
                "deposition_id": deposition.id,
                "doi": deposition_doi,
                "metadata": deposition.meta_data,
                "message": "Deposition succesfully created in Fakenodo"
            }

            return res

        except Exception as ex:
            raise Exception(f"Failed to create deposition in Fakenodo with error: {ex}")

    def uploadFile(self, dataset: DataSet, deposition_id: int, model: FeatureModel, user=None) -> dict:

        if deposition_id not in self.depositions:
            raise Exception("Error 404: Deposition not found.")

        name = model.fm_meta_data.uvl_filename
        author_id = current_user.id
        path = os.path.join(uploads_folder_name(), f"user_{str(author_id)}", f"dataset_{dataset.id}", name)

        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(model.fm_meta_data.uvl_file)("Contenido del archivo simulado en local")

        self.depositions[id]["files"].append(name)

        file_metaData = {
            "file_name": name,
            "file_size": os.path.getsize(path),
            "file_url": f"/uploads/user_{current_user.id}/dataset_{dataset.id}/{name}"
        }
        res = {
            "message": f"File {name} succesfully uploaded to dataset {dataset.id}",
            "file_metadata": file_metaData
        }

        return res

    def publishDeposition(self, deposition_id: int) -> dict:

        deposition = Deposition.query.get(deposition_id)

        if not deposition:
            raise Exception("Error 404: Deposition not found.")

        try:
            deposition["doi"] = f"deposition.doi.{deposition_id}"
            deposition["status"] = "published"

            self.depositions[deposition_id] = deposition

            res = {
                "message": f"Deposition {deposition_id} succesfully published",
                "id": deposition_id,
                "status": "published",
                "doi": deposition["doi"]
            }
            return res
        except Exception as e:
            raise Exception(f"Error publishing deposition {deposition_id}: {str(e)}")

    def getDeposition(self, deposition_id: int) -> dict:

        deposition = Deposition.query.get(deposition_id)

        if not deposition:
            raise Exception("Error 404: Deposition not found.")

        res = self._response(deposition=deposition, metadata=deposition.meta_data,
                             message="Deposition succesfully retrived from fakenodo", doi=deposition.doi)
        return res

    def getDoi(self, deposition_id: int) -> dict:

        deposition = Deposition.query.get(deposition_id)

        if not deposition:
            raise Exception("Error 404: Deposition not found.")

        if "doi" not in deposition.metadata:
            new_doi = self._generateDoi(deposition_id=deposition_id)
            deposition.metadata["doi"] = new_doi

        return deposition.metadata["doi"]

    # Metodos Auxiliares:

    def _buildMetadata(self, dataset: DataSet) -> dict:

        metaData = DSMetaData(dataset.ds_meta_data)
        res = {
            "title": metaData.title,
            "upload_type": "dataset" if metaData.publication_type.value == "none" else "publication",
            "publication_type": metaData.publication_type.value if metaData.publication_type.value != "none" else None,
            "description": metaData.description,
            "creators": [
                {
                    "name": author.name,
                    **({"affiliation": author.affiliation} if author.affiliation else {}),
                    **({"orcid": author.orcid} if author.orcid else {})
                }
                for author in metaData.authors
            ],
            "keywords": ["uvlhub"] if not metaData.tags else metaData.tags.split(", ") + ["uvlhub"],
            "access_right": "open",
            "license": "uvlhub-license"
        }
        return res

    def _generateDoi(self, deposition_id: int) -> str:
        return f"10.5072/UVL{str(deposition_id)}"
