from app.modules.dataset.models import DataSet
from app.modules.fakenodo import fakenodo_bp
from app.modules.fakenodo.services import DepositionService
from app.modules.featuremodel.models import FeatureModel

from flask_login import login_required
from flask import jsonify, request

base_url = "/fakenodo"


# Prueba de conexión
@fakenodo_bp.route(base_url + "/connection", methods=["GET"])
@login_required
def connection():
    """
    Simula la comprobación de conexión a zenodo, siempre da Ok
    """
    res = {
        "status": "OK",
        "message": "Conexión exitosa a Fakenodo"
    }
    return jsonify(res), 200


# Crea una deposición
@fakenodo_bp.route(base_url + "/depositions", methods=["POST"])
@login_required
def create_deposition():
    deposition_service = DepositionService()

    try:
        dataset_id = request.json.get("dataset_id")
        dataset = DataSet.query.get(dataset_id)

        if not dataset:
            return jsonify({"error": "Dataset no encontrado"}), 404

        deposition = deposition_service.createDeposition(dataset=dataset)
        res = {
            "status": "OK",
            "message": "Deposición creada exitosamente",
            "deposition": deposition
        }

        return jsonify(res), 201

    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)}), 500


# Sube un archivo
@fakenodo_bp.route(base_url + "/depositions/<int:deposition_id>", methods=["POST"])
@login_required
def upload_file(deposition_id):
    deposition_service = DepositionService()

    try:
        dataset_id = request.form.get("dataset_id")
        dataset = DataSet.query.get(dataset_id)
        model_id = request.form.get("feature_model_id")
        model = FeatureModel.query.get(model_id)

        if not dataset or not model:
            return jsonify({"error": "Dataset o modelo no encontrado"}), 404

        response = deposition_service.uploadFile(dataset=dataset, deposition_id=deposition_id, model=model)
        res = {
            "status": "OK",
            "message": response["message"],
            "file_metadata": response.get("file_metadata", {})
        }

        return jsonify(res), 201

    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)}), 500


# Publica una deposición
@fakenodo_bp.route(base_url + "/depositions/<int:deposition_id>/publish", methods=["PUT"])
@login_required
def publish_deposition(deposition_id):
    deposition_service = DepositionService()

    try:
        deposition = deposition_service.publishDeposition(deposition_id)
        res = {
            "status": "OK",
            "message": deposition["message"]
        }

        return jsonify(res), 200

    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)}), 500


# Muestra una deposición
@fakenodo_bp.route(base_url + "/depositions/<int:deposition_id>", methods=["GET"])
@login_required
def show_deposition(deposition_id):
    deposition_service = DepositionService()

    try:
        deposition = deposition_service.getDeposition(deposition_id)
        res = {
            "status": "OK",
            "deposition": deposition
        }

        return jsonify(res), 200

    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)}), 500


# Obtiene el doi de una deposición
@fakenodo_bp.route(base_url + "/depositions/<int:deposition_id>/doi", methods=["GET"])
@login_required
def get_deposition_doi(deposition_id):
    deposition_service = DepositionService()

    try:
        doi = deposition_service.getDepositionDOI(deposition_id)
        res = {
            "status": "OK",
            "doi": doi
        }

        return jsonify(res), 200

    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)}), 500


# Obtiene todas las deposiciones
@fakenodo_bp.route(base_url + "/depositions", methods=["GET"])
@login_required
def get_depositions():
    deposition_service = DepositionService()

    try:
        depositions = deposition_service.getDepositions()
        res = {
            "status": "OK",
            "depositions": depositions
        }

        return jsonify(res), 200

    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)}), 500


# Elimina una deposición
@fakenodo_bp.route(base_url + "/depositions/<int:deposition_id>", methods=["DELETE"])
@login_required
def delete_deposition(deposition_id):
    deposition_service = DepositionService()

    try:
        deposition = deposition_service.deleteDeposition(deposition_id)
        res = {
            "status": "OK",
            "message": deposition["message"]
        }
        return jsonify(res), 200

    except Exception as ex:
        return jsonify({"status": "error", "message": str(ex)}), 500
