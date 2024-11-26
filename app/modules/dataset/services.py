import logging
import os
import hashlib
import shutil
from typing import Optional
import uuid

from flask import request
from app import db

from app.modules.auth.services import AuthenticationService
from app.modules.dataset.models import DSViewRecord, DataSet, DSMetaData, DSRating, Author

from app.modules.dataset.repositories import (
    AuthorRepository,
    DOIMappingRepository,
    DSDownloadRecordRepository,
    DSMetaDataRepository,
    DSViewRecordRepository,
    DataSetRepository,
    DSRatingRepository
)
from app.modules.featuremodel.repositories import FMMetaDataRepository, FeatureModelRepository
from app.modules.hubfile.repositories import (
    HubfileDownloadRecordRepository,
    HubfileRepository,
    HubfileViewRecordRepository
)
from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)


def calculate_checksum_and_size(file_path):
    file_size = os.path.getsize(file_path)
    with open(file_path, "rb") as file:
        content = file.read()
        hash_md5 = hashlib.md5(content).hexdigest()
        return hash_md5, file_size


class DataSetService(BaseService):
    def __init__(self):
        super().__init__(DataSetRepository())
        self.feature_model_repository = FeatureModelRepository()
        self.author_repository = AuthorRepository()
        self.dsmetadata_repository = DSMetaDataRepository()
        self.fmmetadata_repository = FMMetaDataRepository()
        self.dsdownloadrecord_repository = DSDownloadRecordRepository()
        self.hubfiledownloadrecord_repository = HubfileDownloadRecordRepository()
        self.hubfilerepository = HubfileRepository()
        self.dsviewrecord_repostory = DSViewRecordRepository()
        self.dsrating_repository = DSRatingRepository()
        self.hubfileviewrecord_repository = HubfileViewRecordRepository()

    def move_feature_models(self, dataset: DataSet):
        current_user = AuthenticationService().get_authenticated_user()
        source_dir = current_user.temp_folder()

        working_dir = os.getenv("WORKING_DIR", "")
        dest_dir = os.path.join(working_dir, "uploads", f"user_{current_user.id}", f"dataset_{dataset.id}")
        os.makedirs(dest_dir, exist_ok=True)
        for feature_model in dataset.feature_models:
            uvl_filename = feature_model.fm_meta_data.uvl_filename
            if not os.path.exists(dest_dir):
                shutil.move(os.path.join(source_dir, uvl_filename), dest_dir)
    def get_synchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_synchronized(current_user_id)

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return self.repository.get_unsynchronized(current_user_id)

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return self.repository.get_unsynchronized_dataset(current_user_id, dataset_id)

    def get_staging_area(self, current_user_id: int) -> DataSet:
        return self.repository.get_staging_area(current_user_id)

    def get_staging_area_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return self.repository.get_staging_area_dataset(current_user_id, dataset_id)

    def latest_synchronized(self):
        return self.repository.latest_synchronized()

    def count_synchronized_datasets(self):
        return self.repository.count_synchronized_datasets()

    def count_feature_models(self):
        return self.feature_model_service.count_feature_models()

    def count_authors(self) -> int:
        return self.author_repository.count()

    def count_dsmetadata(self) -> int:
        return self.dsmetadata_repository.count()

    def total_dataset_downloads(self) -> int:
        return self.dsdownloadrecord_repository.total_dataset_downloads()

    def total_dataset_views(self) -> int:
        return self.dsviewrecord_repostory.total_dataset_views()

    def create_from_form(self, form, current_user, staging_area) -> DataSet:
        main_author = {
            "name": f"{current_user.profile.surname}, {current_user.profile.name}",
            "affiliation": current_user.profile.affiliation,
            "orcid": current_user.profile.orcid,
        }
        try:
            logger.info(f"Creating dsmetadata...: {form.get_dsmetadata()}")
            dsmetadata = self.dsmetadata_repository.create(**form.get_dsmetadata())
            if not staging_area:
                dsmetadata.staging_area = False
            for author_data in [main_author] + form.get_authors():
                author = self.author_repository.create(commit=False, ds_meta_data_id=dsmetadata.id, **author_data)
                dsmetadata.authors.append(author)

            dataset = self.create(commit=False, user_id=current_user.id, ds_meta_data_id=dsmetadata.id)

            for feature_model in form.feature_models:
                uvl_filename = feature_model.uvl_filename.data
                fmmetadata = self.fmmetadata_repository.create(commit=False, **feature_model.get_fmmetadata())
                for author_data in feature_model.get_authors():
                    author = self.author_repository.create(commit=False, fm_meta_data_id=fmmetadata.id, **author_data)
                    fmmetadata.authors.append(author)

                fm = self.feature_model_repository.create(
                    commit=False, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
                )

                # associated files in feature model
                file_path = os.path.join(current_user.temp_folder(), uvl_filename)
                checksum, size = calculate_checksum_and_size(file_path)

                file = self.hubfilerepository.create(
                    commit=False, name=uvl_filename, checksum=checksum, size=size, feature_model_id=fm.id
                )
                fm.files.append(file)
            self.repository.session.commit()
        except Exception as exc:
            logger.info(f"Exception creating dataset from form...: {exc}")
            self.repository.session.rollback()
            raise exc
        return dataset
    def update_from_form(self, dataset: DataSet, form, current_user):
        dataset.ds_meta_data.title = form.title.data
        dataset.ds_meta_data.description = form.desc.data
        dataset.ds_meta_data.publication_type = form.publication_type.data
        dataset.ds_meta_data.publication_doi = form.publication_doi.data
        dataset.ds_meta_data.dataset_doi = form.dataset_doi.data
        dataset.ds_meta_data.tags = form.tags.data

        # Update authors
        dataset.ds_meta_data.authors = []
        for author_form in form.authors.entries:
            author = Author(
                name=author_form.name.data,
                affiliation=author_form.affiliation.data,
                orcid=author_form.orcid.data
            )
            dataset.ds_meta_data.authors.append(author)

        for feature_model in dataset.feature_models:
            db.session.delete(feature_model)

        # Luego, commit para reflejar los cambios (si es necesario)
        db.session.commit()
    # Actualizar o agregar nuevos FeatureModels
        for feature_model in form.feature_models:
            uvl_filename = feature_model.uvl_filename.data
            fmmetadata = self.fmmetadata_repository.create(commit=True, **feature_model.get_fmmetadata())
            for author_data in feature_model.get_authors():
                author = self.author_repository.create(commit=True, fm_meta_data_id=fmmetadata.id, **author_data)
                fmmetadata.authors.append(author)

            fm = self.feature_model_repository.create(
                commit=True, data_set_id=dataset.id, fm_meta_data_id=fmmetadata.id
            )

            # Ahora, podemos asociar el nuevo archivo como lo hacías antes.
            file_path = os.path.join(current_user.temp_folder(), uvl_filename)
            checksum, size = calculate_checksum_and_size(file_path)

            file = self.hubfilerepository.create(
                commit=False, name=uvl_filename, checksum=checksum, size=size, feature_model_id=fm.id
            )
            fm.files.append(file)

        self.repository.session.commit()
        return dataset

    def update_dsmetadata(self, id, **kwargs):
        return self.dsmetadata_repository.update(id, **kwargs)

    def get_uvlhub_doi(self, dataset: DataSet) -> str:
        domain = os.getenv('DOMAIN', 'localhost')
        return f'http://{domain}/doi/{dataset.ds_meta_data.dataset_doi}'


class AuthorService(BaseService):
    def __init__(self):
        super().__init__(AuthorRepository())


class DSDownloadRecordService(BaseService):
    def __init__(self):
        super().__init__(DSDownloadRecordRepository())


class DSMetaDataService(BaseService):
    def __init__(self):
        super().__init__(DSMetaDataRepository())

    def update(self, id, **kwargs):
        return self.repository.update(id, **kwargs)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.repository.filter_by_doi(doi)


class DSViewRecordService(BaseService):
    def __init__(self):
        super().__init__(DSViewRecordRepository())

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.repository.the_record_exists(dataset, user_cookie)

    def create_new_record(self, dataset: DataSet,  user_cookie: str) -> DSViewRecord:
        return self.repository.create_new_record(dataset, user_cookie)

    def create_cookie(self, dataset: DataSet) -> str:

        user_cookie = request.cookies.get("view_cookie")
        if not user_cookie:
            user_cookie = str(uuid.uuid4())

        existing_record = self.the_record_exists(dataset=dataset, user_cookie=user_cookie)

        if not existing_record:
            self.create_new_record(dataset=dataset, user_cookie=user_cookie)

        return user_cookie


class DOIMappingService(BaseService):
    def __init__(self):
        super().__init__(DOIMappingRepository())

    def get_new_doi(self, old_doi: str) -> str:
        doi_mapping = self.repository.get_new_doi(old_doi)
        if doi_mapping:
            return doi_mapping.dataset_doi_new
        else:
            return None


class DSRatingService(BaseService):
    def __init__(self):
        super().__init__(DSRatingRepository())

    def add_or_update_rating(self, dsmetadata_id: int, user_id: int, rating_value: int) -> DSRating:
        rating = self.repository.get_user_rating(dsmetadata_id, user_id)
        if rating:
            print(f"Actualizando rating a {rating_value}")
            rating.rating = rating_value
        else:
            print("Valor de rating en el servicio:", rating_value)
            rating = self.repository.create(commit=False, ds_meta_data_id=dsmetadata_id, user_id=user_id, rating=rating_value)
            print("Valor de rating en el servicio:", rating.rating)
        self.repository.session.commit()
        return rating

    def get_dataset_average_rating(self, dsmetadata_id: int) -> float:
        return self.repository.get_average_rating(dsmetadata_id)

    def get_total_ratings(self, dsmetadata_id: int) -> int:
        return self.repository.count_ratings(dsmetadata_id)


class SizeService():

    def __init__(self):
        pass

    def get_human_readable_size(self, size: int) -> str:
        if size < 1024:
            return f'{size} bytes'
        elif size < 1024 ** 2:
            return f'{round(size / 1024, 2)} KB'
        elif size < 1024 ** 3:
            return f'{round(size / (1024 ** 2), 2)} MB'
        else:
            return f'{round(size / (1024 ** 3), 2)} GB'
