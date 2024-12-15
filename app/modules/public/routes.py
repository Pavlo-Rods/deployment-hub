from flask import render_template
from app.modules.featuremodel.services import FeatureModelService
from app.modules.public import public_bp
from app.modules.dataset.services import DataSetService
import logging
from flask import jsonify

logger = logging.getLogger(__name__)


@public_bp.route("/")
def index():
    logger.info("Access index")
    dataset_service = DataSetService()
    feature_model_service = FeatureModelService()

    datasets_counter = dataset_service.count_synchronized_datasets()
    feature_models_counter = feature_model_service.count_feature_models()

    total_dataset_downloads = dataset_service.total_dataset_downloads()
    total_feature_model_downloads = feature_model_service.total_feature_model_downloads()

    total_dataset_views = dataset_service.total_dataset_views()
    total_feature_model_views = feature_model_service.total_feature_model_views()

    return render_template(
        "public/index.html",
        datasets=dataset_service.latest_synchronized(),
        datasets_counter=datasets_counter,
        feature_models_counter=feature_models_counter,
        total_dataset_downloads=total_dataset_downloads,
        total_feature_model_downloads=total_feature_model_downloads,
        total_dataset_views=total_dataset_views,
        total_feature_model_views=total_feature_model_views
    )


@public_bp.route("/dashboard")
def dashboard():
    try:
        dataset_service = DataSetService()
        feature_model_service = FeatureModelService()

        datasets_counter = dataset_service.count_synchronized_datasets()
        feature_models_counter = feature_model_service.count_feature_models()

        total_dataset_downloads = dataset_service.total_dataset_downloads()
        total_feature_model_downloads = feature_model_service.total_feature_model_downloads()

        total_dataset_views = dataset_service.total_dataset_views()
        total_feature_model_views = feature_model_service.total_feature_model_views()

        return render_template(
            "dashboard.html",
            datasets_counter=datasets_counter,
            feature_models_counter=feature_models_counter,
            total_dataset_downloads=total_dataset_downloads,
            total_feature_model_downloads=total_feature_model_downloads,
            total_dataset_views=total_dataset_views,
            total_feature_model_views=total_feature_model_views
        )

    except Exception as e:
        print(f"Error en la obtención de datos para el dashboard: {str(e)}")
        return jsonify({"error": f"Hubo un problema al obtener los datos: {str(e)}"}), 500
