import logging
import os
import re
import shutil
import tempfile
import uuid
from datetime import datetime, timezone
from zipfile import ZipFile

from flask import (
    redirect,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
    abort,
    url_for,
)
from flask_login import login_required, current_user

from app.modules.dataset.forms import DataSetForm
from app.modules.dataset.models import (
    DSDownloadRecord
)
from app.modules.dataset import dataset_bp
from app.modules.dataset.services import (
    AuthorService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
    DataSetService,
    DOIMappingService,
    RatingService
)

from app.modules.fakenodo.services import DepositionService
from core.configuration.configuration import USE_FAKENODO

logger = logging.getLogger(__name__)


dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
fakenodo_service = DepositionService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def create_dataset():
    form = DataSetForm()
    if request.method == "POST":

        dataset = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user)
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        if USE_FAKENODO:
            try:
                publication_doi = form.publication_doi.data if form.publication_doi.data else None

                response = fakenodo_service.createDeposition(dataset=dataset, doi=publication_doi)

                if 'deposition_id' in response:
                    deposition_id = response.get("deposition_id")

                    if "doi" in response:
                        doi = response.get("doi")
                        dataset_service.update_dsmetadata(dataset.ds_meta_data,
                                                          deposition_id=deposition_id, dataset_doi=doi)
                    else:
                        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

                    res = {
                        "status": "OK",
                        "message": "Dataset uploaded successfullyand DOI generated",
                        "doi": doi
                    }
                    return jsonify(res), 200

                else:
                    return jsonify({"status": "error", "message": "Failed to create deposition, not all data was sent"
                                    }), 500

            except Exception as e:
                msg = f"it has not been possible upload feature models in Fakenodo and update the DOI: {e}"
                return jsonify({"message": msg}), 200

        # Delete temp folder
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Everything works!"
        return jsonify({"message": msg}), 200

    return render_template("dataset/upload_dataset.html", form=form, use_fakenodo=USE_FAKENODO)


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()
    doi = request.form.get("publication_doi")

    if not file or not file.filename.endswith(".uvl"):
        return jsonify({"message": "No valid file"}), 400

    if doi:
        if not re.match(r"^10\.\d{4}$", doi):
            return jsonify({"message": "DOI invalido, tiene que ser de la forma 10.XXXX"}), 400

    # create temp folder
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    file_path = os.path.join(temp_folder, file.filename)

    if os.path.exists(file_path):
        # Generate unique filename (by recursion)
        base_name, extension = os.path.splitext(file.filename)
        i = 1
        while os.path.exists(
            os.path.join(temp_folder, f"{base_name} ({i}){extension}")
        ):
            i += 1
        new_filename = f"{base_name} ({i}){extension}"
        file_path = os.path.join(temp_folder, new_filename)
    else:
        new_filename = file.filename

    try:
        file.save(file_path)
    except Exception as e:
        return jsonify({"message": str(e)}), 500

    return (
        jsonify(
            {
                "message": "UVL uploaded and validated successfully",
                "filename": new_filename,
            }
        ),
        200,
    )


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
def delete():
    data = request.get_json()
    filename = data.get("file")
    temp_folder = current_user.temp_folder()
    filepath = os.path.join(temp_folder, filename)

    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({"message": "File deleted successfully"})

    return jsonify({"error": "Error: File not found"})


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)

    file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"dataset_{dataset_id}.zip")

    with ZipFile(zip_path, "w") as zipf:
        for subdir, dirs, files in os.walk(file_path):
            for file in files:
                full_path = os.path.join(subdir, file)

                relative_path = os.path.relpath(full_path, file_path)

                zipf.write(
                    full_path,
                    arcname=os.path.join(
                        os.path.basename(zip_path[:-4]), relative_path
                    ),
                )

    user_cookie = request.cookies.get("download_cookie")
    if not user_cookie:
        user_cookie = str(
            uuid.uuid4()
        )  # Generate a new unique identifier if it does not exist
        # Save the cookie to the user's browser
        resp = make_response(
            send_from_directory(
                temp_dir,
                f"dataset_{dataset_id}.zip",
                as_attachment=True,
                mimetype="application/zip",
            )
        )
        resp.set_cookie("download_cookie", user_cookie)
    else:
        resp = send_from_directory(
            temp_dir,
            f"dataset_{dataset_id}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

    # Check if the download record already exists for this cookie
    existing_record = DSDownloadRecord.query.filter_by(
        user_id=current_user.id if current_user.is_authenticated else None,
        dataset_id=dataset_id,
        download_cookie=user_cookie
    ).first()

    if not existing_record:
        # Record the download in your database
        DSDownloadRecordService().create(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset_id,
            download_date=datetime.now(timezone.utc),
            download_cookie=user_cookie,
        )

    return resp


@dataset_bp.route("/doi/<path:doi>", methods=["GET"])
def subdomain_index(doi):

    # Check if the DOI is an old DOI
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        # Redirect to the same path with the new DOI
        return redirect(url_for('dataset.subdomain_index', doi=new_doi), code=302)

    # Try to search the dataset by the provided DOI (which should already be the new one)
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    # Get dataset
    dataset = ds_meta_data.data_set

    # Save the cookie to the user's browser
    # Calcula el promedio de valoraciones del dataset
    average_rating = RatingService.get_average_rating(dataset.id)
    # Asegúrate de que `get_average_rating` esté bien implementado
    # Calcula y asigna la media de valoración para cada modelo
    for model in dataset.feature_models:
        model.average_rating = RatingService.get_average_model_rating(model.id)
    # Renderiza la plantilla pasando los valores calculados
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset, average_rating=average_rating))
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/download_all_datasets", methods=["GET"])
def download_all_datasets():
    try:

        datasets = dataset_service.download_all_datasets()

        if not datasets:
            return jsonify({"error": "No datasets found."}), 404

        temp_dir = create_temp_dir()
        zip_path = os.path.join(temp_dir, "allDatasets.zip")

        # Crear el archivo ZIP
        create_zip_of_datasets(datasets, zip_path)

        # Enviar el archivo ZIP
        return send_from_directory(
            temp_dir,
            "allDatasets.zip",
            as_attachment=True,
            mimetype="application/zip"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:

        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir)


def create_temp_dir():
    # Crea un directorio temporal
    return tempfile.mkdtemp()


def create_zip_of_datasets(datasets, zip_path):
    # Creamos el Zip
    with ZipFile(zip_path, "w") as zipf:
        for dataset in datasets:
            file_path = f"uploads/user_{dataset.user_id}/dataset_{dataset.id}/"

            if not os.path.exists(file_path):
                continue

            for subdir, dirs, files in os.walk(file_path):
                for file in files:
                    full_path = os.path.join(subdir, file)
                    relative_path = os.path.relpath(full_path, file_path)
                    arcname = os.path.join(f"dataset_{dataset.id}", relative_path)
                    zipf.write(full_path, arcname=arcname)


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    return render_template("dataset/view_dataset.html", dataset=dataset)


@dataset_bp.route('/dataset/synchronize_datasets', methods=['POST'])
@login_required
def synchronize_datasets():
    try:
        # Obtener los datos enviados desde el frontend
        data = request.get_json()
        print("Datos recibidos:", data)  # Log para verificar los datos recibidos

        # Verificar que datasetId esté presente
        dataset_id = int(data.get("datasetId"))

        if not dataset_id:
            print("Error: No se recibió el datasetId.")  # Si el datasetId es None o no está presente
            return jsonify({"message": "El datasetId es requerido."}), 400

        print("datasetId recibido:", dataset_id)  # Log para verificar que se recibe el datasetId correctamente

        # Llamar al servicio para sincronizar los datasets con el datasetId
        dataset_service.synchronize_unsynchronized_datasets(current_user.id, dataset_id)

        return jsonify({"success": True, "message": "Datasets sincronizados correctamente."}), 200
    except Exception as e:
        print("Error:", e)  # Log para mostrar el error específico
        return jsonify({"message": str(e)}), 400


@dataset_bp.route('/dataset/rate', methods=['POST'])
@login_required
def rate_dataset():
    user_id = current_user.id
    dataset_id = request.form.get('dataset_id')
    rating = int(request.form.get('rating'))

    # Instancia del servicio de valoraciones
    rating_service = RatingService()
    rating_service.add_rating(user_id, dataset_id, rating)

    # Calcula el promedio actualizado
    average_rating = rating_service.get_average_rating(dataset_id)

    # Devuelve el promedio en JSON
    return jsonify({'average_rating': average_rating}), 200
