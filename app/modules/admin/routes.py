from flask import render_template, abort
from flask_login import login_required, current_user
from app.modules.admin import admin_bp
from app.modules.featuremodel.services import FeatureModelService
from app.modules.dataset.services import DataSetService
from app.modules.hubfile.services import HubfileService, HubfileDownloadRecordService
from app.modules.auth.services import AuthenticationService
from app.modules.charts.charts import plot_downloads_bar_chart, plot_users_with_most_downloads, plot_feature_models_with_most_downloads



@admin_bp.route('/admin', methods=['GET'])
def index():
    return render_template('admin/index.html')


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        abort(403)  # Raise a 403 Forbidden exception
        # raise Exception("Access denied: you don't have authorization.")

    dataset_service = DataSetService()
    feature_model_service = FeatureModelService()
    hubfile_download_service= HubfileDownloadRecordService()
    auth_service = AuthenticationService()

    # Statistics: total datasets and feature models
    datasets_counter = dataset_service.count_synchronized_datasets()
    feature_models_counter = feature_model_service.count_feature_models()

    # Statistics: total downloads
    total_dataset_downloads = dataset_service.total_dataset_downloads()
    total_feature_model_downloads = feature_model_service.total_feature_model_downloads()
    fm_downloads = hubfile_download_service.features_models_with_most_downloads()
    max_downloads = dataset_service.max_downloads()
    #datasets_with_most_downloads = dataset_service.datasets_with_most_downloads()
    user_downloads = dataset_service.user_max_downloads()

    # Statistics: total views
    total_dataset_views = dataset_service.total_dataset_views()
    total_feature_model_views = feature_model_service.total_feature_model_views()

    # Statistics: total users
    users_counter = auth_service.count_total_users()
    admin_user_counter = auth_service.count_total_admin_users()

    # Plot datasets with most dowloads
    dataset_names, download_counts = dataset_service.datasets_with_most_downloads()
    plot_url = plot_downloads_bar_chart(dataset_names, download_counts)

    #Plot users with most downloads
    users_email, downloads = dataset_service.users_with_most_downloads()
    plot_users = plot_users_with_most_downloads(users_email, downloads)

    #Plot feature models with most downloads
    features_title, download_feature = hubfile_download_service.features_models_with_most_downloads()
    plot_features_downloads = plot_feature_models_with_most_downloads(features_title, download_feature)

    return render_template(
        "admin/dashboard.html",
        datasets=dataset_service.latest_synchronized(),
        datasets_counter=datasets_counter,
        feature_models_counter=feature_models_counter,
        total_dataset_downloads=total_dataset_downloads,
        total_feature_model_downloads=total_feature_model_downloads,
        total_dataset_views=total_dataset_views,
        total_feature_model_views=total_feature_model_views,
        fm_downloads = fm_downloads,
        users_counter=users_counter,
        admin_user_counter=admin_user_counter,
        max_downloads_dataset=max_downloads[0],
        max_downloads=max_downloads[1],
        #datasets_with_most_downloads = datasets_with_most_downloads,
        user_downloads=user_downloads[0],
        number_downloads_user=user_downloads[1],
        plot_url=plot_url,
        plot_users = plot_users,
        plot_features_downloads = plot_features_downloads
    )
