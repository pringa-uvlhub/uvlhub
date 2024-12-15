import logging
import os
import json
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
from app.modules.dataset.forms import FeatureModelForm
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
    DSRatingService
)
from app.modules.zenodo.services import ZenodoService
from app.modules.fakenodo.services import FakenodoService
from app.modules.dataset.repositories import (
    DSMetaDataRepository,
    DataSetRepository
)


logger = logging.getLogger(__name__)

metadata_repository = DSMetaDataRepository()
dataset_repository = DataSetRepository()
dataset_service = DataSetService()
author_service = AuthorService()
dsmetadata_service = DSMetaDataService()
zenodo_service = ZenodoService()
fakenodo_service = FakenodoService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()
ds_rating_service = DSRatingService()


@dataset_bp.route("/dataset/upload", methods=["GET", "POST"])
@login_required
def upload_dataset_zenodo():
    form = DataSetForm()
    if request.method == "POST":

        dataset = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user, staging_area=False)
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        # send dataset as deposition to Zenodo
        data = {}
        try:
            zenodo_response_json = zenodo_service.create_new_deposition(dataset)
            response_data = json.dumps(zenodo_response_json)
            data = json.loads(response_data)
        except Exception as exc:
            data = {}
            zenodo_response_json = {}
            logger.exception(f"Exception while create dataset data in Zenodo {exc}")

        if data.get("conceptrecid"):
            deposition_id = data.get("id")

            # update dataset with deposition id in Zenodo
            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

            try:
                # iterate for each feature model (one feature model = one request to Zenodo)
                for feature_model in dataset.feature_models:
                    zenodo_service.upload_file(dataset, deposition_id, feature_model)

                # publish deposition
                zenodo_service.publish_deposition(deposition_id)

                # update DOI
                deposition_doi = zenodo_service.get_doi(deposition_id)
                dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
            except Exception as e:
                msg = f"it has not been possible upload feature models in Zenodo and update the DOI: {e}"
                return jsonify({"message": msg}), 200

        # Delete temp folder
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Everything works!"
        return jsonify({"message": msg}), 200

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/upload-fakenodo", methods=["POST"])
@login_required
def upload_dataset_fakenodo():
    form = DataSetForm()
    if request.method == "POST":

        dataset = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user, staging_area=False)
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        try:
            fakenodo_response_json = fakenodo_service.create_new_deposition(dataset)
            fakenodo_ds_doi = fakenodo_response_json.get("fakenodo_doi")
        except Exception as exc:
            fakenodo_response_json = {}
            logger.exception(f"Exception while create dataset data in Fakenodo {exc}")

        # update dataset with new fakenodo doi
        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_fakenodo_doi=fakenodo_ds_doi)

        # Delete temp folder
        file_path = current_user.temp_folder()
        if os.path.exists(file_path) and os.path.isdir(file_path):
            shutil.rmtree(file_path)

        msg = "Everything works!"
        return jsonify({"message": msg}), 200


@dataset_bp.route("/dataset/upload-fakenodo/<int:dataset_id>", methods=["POST"])
@login_required
def upload_dataset_fakenodo_from_staging(dataset_id):
    form = DataSetForm()
    dataset = dataset_service.get_staging_area_dataset(current_user.id, dataset_id)
    if not dataset:
        abort(404)

    if not form.validate_on_submit():
        print("Form errors:", form.errors)
        return jsonify({"message": form.errors}), 400

    dataset.ds_meta_data.staging_area = False
    dataset.ds_meta_data.build = False
    dataset = dataset_service.update_from_form(dataset, form, current_user)
    dataset_service.move_feature_models(dataset)

    try:
        fakenodo_response_json = fakenodo_service.create_new_deposition(dataset)
        fakenodo_ds_doi = fakenodo_response_json.get("fakenodo_doi")
    except Exception as exc:
        fakenodo_response_json = {}
        logger.exception(f"Exception while create dataset data in Fakenodo {exc}")

    # update dataset with new fakenodo doi
    dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_fakenodo_doi=fakenodo_ds_doi)

    # Delete temp folder
    file_path = current_user.temp_folder()
    if os.path.exists(file_path) and os.path.isdir(file_path):
        shutil.rmtree(file_path)

    msg = "Everything works!"
    return jsonify({"message": msg}), 200


@dataset_bp.route("/dataset/upload/<int:dataset_id>", methods=["POST"])
@login_required
def upload_dataset_zenodo_from_staging(dataset_id):
    form = DataSetForm()
    dataset = dataset_service.get_staging_area_dataset(current_user.id, dataset_id)
    if not dataset:
        abort(404)

    if not form.validate_on_submit():
        print("Form errors:", form.errors)
        return jsonify({"message": form.errors}), 400
    dataset.ds_meta_data.staging_area = False
    dataset.ds_meta_data.build = False
    dataset = dataset_service.update_from_form(dataset, form, current_user)
    dataset_service.move_feature_models(dataset)
    data = {}
    try:
        zenodo_response_json = zenodo_service.create_new_deposition(dataset)
        response_data = json.dumps(zenodo_response_json)
        data = json.loads(response_data)
    except Exception as exc:
        data = {}
        zenodo_response_json = {}
        logger.exception(f"Exception while create dataset data in Zenodo {exc}")

    if data.get("conceptrecid"):
        deposition_id = data.get("id")

        # update dataset with deposition id in Zenodo
        dataset_service.update_dsmetadata(dataset.ds_meta_data_id, deposition_id=deposition_id)

        try:
            # iterate for each feature model (one feature model = one request to Zenodo)
            for feature_model in dataset.feature_models:
                zenodo_service.upload_file(dataset, deposition_id, feature_model)

            # publish deposition
            zenodo_service.publish_deposition(deposition_id)

            # update DOI
            deposition_doi = zenodo_service.get_doi(deposition_id)
            dataset_service.update_dsmetadata(dataset.ds_meta_data_id, dataset_doi=deposition_doi)
        except Exception as e:
            msg = f"it has not been possible upload feature models in Zenodo and update the DOI: {e}"
            return jsonify({"message": msg}), 200

    # Delete temp folder
    file_path = current_user.temp_folder()
    if os.path.exists(file_path) and os.path.isdir(file_path):
        shutil.rmtree(file_path)

    msg = "Everything works!"
    return jsonify({"message": msg}), 200


@dataset_bp.route("/dataset/create", methods=["POST"])
@login_required
def create_dataset():
    form = DataSetForm()
    if request.method == "POST":
        dataset = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating dataset...")
            dataset = dataset_service.create_from_form(form=form, current_user=current_user, staging_area=True)
            logger.info(f"Created dataset: {dataset}")
            dataset_service.move_feature_models(dataset)
        except Exception as exc:
            logger.exception(f"Exception while create dataset data in local {exc}")
            return jsonify({"Exception while create dataset data in local: ": str(exc)}), 400

        msg = "Everything works!"
        return jsonify({"message": msg}), 200

    return render_template("dataset/upload_dataset.html", form=form)


@dataset_bp.route("/dataset/staging-area/<int:dataset_id>", methods=["GET", "POST"])
@login_required
def update_staging_area_dataset(dataset_id):
    dataset = dataset_service.get_staging_area_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)
    form = DataSetForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                dataset_service.update_from_form(dataset, form, current_user)
                dataset_service.move_feature_models(dataset)
                return redirect(url_for('dataset.update_staging_area_dataset', dataset_id=dataset_id))
            except Exception as exc:
                print(dataset.feature_models)
                logger.exception(f"Exception while updating dataset: {exc}")
                return jsonify({"Exception while updating dataset: ": str(exc)}), 400
        else:
            print("Form errors:", form.errors)
            return jsonify({"message": form.errors}), 400

    if request.method == 'GET':
        form.title.data = dataset.ds_meta_data.title
        form.desc.data = dataset.ds_meta_data.description
        form.publication_type.data = dataset.ds_meta_data.publication_type.value
        form.publication_doi.data = dataset.ds_meta_data.publication_doi
        form.dataset_doi.data = dataset.ds_meta_data.dataset_doi
        form.tags.data = dataset.ds_meta_data.tags
        form.feature_models.entries = [FeatureModelForm(obj=fm.fm_meta_data) for fm
                                       in dataset.feature_models]
        feature_models = dataset.feature_models
        feature_models_data = [
            {
                'title': fm.fm_meta_data.title,
                'files': [{'name': file.name, 'size': file.size} for file in fm.files]
            }
            for fm in feature_models
        ]
        return render_template("dataset/upload_dataset.html", dataset=dataset, form=form,
                               feature_models=feature_models_data)


@dataset_bp.route("/dataset/delete/<int:dataset_id>", methods=["DELETE"])
@login_required
def delete_dataset(dataset_id):
    dataset = dataset_service.get_staging_area_dataset(current_user.id, dataset_id)
    if not dataset:
        abort(404, description="Dataset not found")

    if dataset.user_id != current_user.id:
        abort(403, description="You do not have permission to delete this dataset")

    try:
        dataset_service.delete(dataset_id)
        temp_folder = os.path.join('uploads', f'user_{current_user.id}', f'dataset_{dataset_id}')
        if os.path.exists(temp_folder) and os.path.isdir(temp_folder):
            shutil.rmtree(temp_folder)

        return jsonify({"message": "Dataset deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": f"An error occurred while deleting the dataset: {str(e)}"}), 500


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        fakenodo_datasets=dataset_service.get_fakenodo_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
        unprepared_datasets=dataset_service.get_staging_area(current_user.id),
    )


@dataset_bp.route("/dataset/build_empty/<int:feature_model_id>", methods=["POST"])
@login_required
def create_empty_dataset(feature_model_id):
    print("12")
    try:
        dataset = dataset_service.create_empty_dataset(current_user=current_user, feature_model_id=feature_model_id)
        logger.info(f"Created empty dataset: {dataset}")

        return jsonify({
            "message": "Empty dataset created successfully and UVL file added.",
            "dataset_id": dataset.id
        }), 200
    except Exception as exc:
        # En caso de error, capturamos la excepción y respondemos con un mensaje adecuado
        logger.exception(f"Exception while processing dataset: {exc}")
        return jsonify({"error": "Exception while processing dataset", "details": str(exc)}), 400


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    file = request.files["file"]
    temp_folder = current_user.temp_folder()

    if not file or not file.filename.endswith(".uvl"):
        return jsonify({"message": "No valid file"}), 400

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
    print(data)
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


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
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
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset))
    resp.set_cookie("view_cookie", user_cookie)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    print(dataset.to_dict())

    return render_template("dataset/view_dataset.html", dataset=dataset)


@dataset_bp.route("/dataset/fakenodo-synchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_fakenodo_synchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_fakenodo_synchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    print(dataset.to_dict())

    return render_template("dataset/view_dataset.html", dataset=dataset)


@dataset_bp.route("/datasets/<int:dataset_id>/rate", methods=["POST"])
@login_required
def rate_dataset(dataset_id):
    user_id = current_user.id

    try:
        rating_value = float(request.json.get('rating'))

        if not (0 <= rating_value <= 5) or rating_value != rating_value \
                or not float('-inf') < rating_value < float('inf'):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid rating value. Must be a finite number between 0 and 5.'}), 400

    rating = ds_rating_service.add_or_update_rating(dataset_id, user_id, rating_value)
    return jsonify({'message': 'Rating added', 'rating': rating.to_dict()}), 200


@dataset_bp.route('/datasets/<int:dataset_id>/average-rating', methods=['GET'])
def get_dataset_average_rating(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)
    average_rating = ds_rating_service.get_dataset_average_rating(dataset.id)
    return jsonify({'average_rating': average_rating}), 200
