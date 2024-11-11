from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.modules.admin import admin_bp
from app.modules.featuremodel.services import FeatureModelService
from app.modules.dataset.services import DataSetService
from app.modules.auth.services import AuthenticationService


@admin_bp.route('/admin', methods=['GET'])
def index():
    return render_template('admin/index.html')


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('public.index'))

    dataset_service = DataSetService()
    feature_model_service = FeatureModelService()
    auth_service = AuthenticationService()

    # Statistics: total datasets and feature models
    datasets_counter = dataset_service.count_synchronized_datasets()
    feature_models_counter = feature_model_service.count_feature_models()

    # Statistics: total downloads
    total_dataset_downloads = dataset_service.total_dataset_downloads()
    total_feature_model_downloads = feature_model_service.total_feature_model_downloads()

    # Statistics: total views
    total_dataset_views = dataset_service.total_dataset_views()
    total_feature_model_views = feature_model_service.total_feature_model_views()

    # Statistics: total users
    users_counter = auth_service.count_total_users()
    admin_user_counter = auth_service.count_total_admin_users()

    return render_template(
        "admin/dashboard.html",
        datasets=dataset_service.latest_synchronized(),
        datasets_counter=datasets_counter,
        feature_models_counter=feature_models_counter,
        total_dataset_downloads=total_dataset_downloads,
        total_feature_model_downloads=total_feature_model_downloads,
        total_dataset_views=total_dataset_views,
        total_feature_model_views=total_feature_model_views,
        users_counter=users_counter,
        admin_user_counter=admin_user_counter
    )
