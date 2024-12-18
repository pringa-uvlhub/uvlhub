from datetime import datetime, timezone
import logging
from flask_login import current_user
from typing import Optional

from sqlalchemy import desc, func

from app.modules.dataset.models import (
    Author,
    DOIMapping,
    DSDownloadRecord,
    DSMetaData,
    DSViewRecord,
    DataSet,
    DSRating
)
from core.repositories.BaseRepository import BaseRepository
from app.modules.auth.repositories import UserRepository

logger = logging.getLogger(__name__)


class AuthorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Author)


class DSDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSDownloadRecord)

    def total_dataset_downloads(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def max_downloads(self):
        download_count = {}
        for download in self.model.query.all():
            if download.dataset_id in download_count:
                download_count[download.dataset_id] += 1
            else:
                download_count[download.dataset_id] = 1
        if not download_count:
            return None  # O algún valor por defecto apropiado
        max_dataset_id = max(download_count, key=download_count.get)
        dataset_repo = DataSetRepository()
        max_dataset = dataset_repo.get_dataset_by_id(max_dataset_id)
        return max_dataset, download_count[max_dataset_id]

    def datasets_with_most_downloads(self):
        download_count = {}
        for download in self.model.query.all():
            if download.dataset_id in download_count:
                download_count[download.dataset_id] += 1
            else:
                download_count[download.dataset_id] = 1
        most_downloaded_datasets = sorted(download_count.items(), key=lambda x: x[1], reverse=True)[:5]
        datasets = []
        dataset_names = []
        download_counts = []

        for dataset_id, count in most_downloaded_datasets:
            dataset_repo = DataSetRepository()
            dataset = dataset_repo.get_dataset_by_id(dataset_id)
            datasets.append((dataset, count))
            dataset_names.append(dataset.name())  # Asegúrate de que `dataset` tenga un atributo `name`
            download_counts.append(count)

        return dataset_names, download_counts

    def users_with_most_downloads(self):
        download_count = {}
        for download in self.model.query.all():
            if download.user_id in download_count:
                download_count[download.user_id] += 1
            else:
                download_count[download.user_id] = 1
        if not download_count:
            return None
        user_with_most_downloads = sorted(download_count.items(), key=lambda x: x[1], reverse=True)[:5]
        users = []
        user_email = []
        download_counts = []
        for user_id, count in user_with_most_downloads:
            user_repo = UserRepository()
            user = user_repo.get_user_by_id(user_id)
            users.append((user, count))
            user_email.append(user.email)
            download_counts.append(count)
        return user_email, download_counts

    def user_max_downloads(self):
        download_count = {}
        for download in self.model.query.all():
            if download.user_id in download_count:
                download_count[download.user_id] += 1
            else:
                download_count[download.user_id] = 1
        if not download_count:
            return None  # O algún valor por defecto apropiado
        max_user_id = max(download_count, key=download_count.get)

        user_repo = UserRepository()
        max_user = user_repo.get_user_by_id(max_user_id)
        return max_user, download_count[max_user_id]


class DSMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSMetaData)

    def filter_by_doi(self, doi: str) -> Optional[DSMetaData]:
        return self.model.query.filter_by(dataset_doi=doi).first()

    def filter_by_build(self) -> Optional[DSMetaData]:
        return self.model.query.filter_by(build=True).first()


class DSViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSViewRecord)

    def total_dataset_views(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def the_record_exists(self, dataset: DataSet, user_cookie: str):
        return self.model.query.filter_by(
            user_id=current_user.id if current_user.is_authenticated else None,
            dataset_id=dataset.id,
            view_cookie=user_cookie
        ).first()

    def create_new_record(self, dataset: DataSet, user_cookie: str) -> DSViewRecord:
        return self.create(
                user_id=current_user.id if current_user.is_authenticated else None,
                dataset_id=dataset.id,
                view_date=datetime.now(timezone.utc),
                view_cookie=user_cookie,
            )

    def datasets_with_most_views(self):
        view_count = {}
        for view in self.model.query.all():
            if view.dataset_id in view_count:
                view_count[view.dataset_id] += 1
            else:
                view_count[view.dataset_id] = 1

        most_viewed_datasets = sorted(view_count.items(), key=lambda x: x[1], reverse=True)[:5]
        datasets = []
        dataset_names = []
        view_counts = []

        for dataset_id, count in most_viewed_datasets:
            dataset_repo = DataSetRepository()
            dataset = dataset_repo.get_dataset_by_id(dataset_id)
            datasets.append((dataset, count))
            dataset_names.append(dataset.name())
            view_counts.append(count)
        return dataset_names, view_counts


class DataSetRepository(BaseRepository):
    def __init__(self):
        super().__init__(DataSet)

    def get_synchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.isnot(None),
                    DSMetaData.dataset_fakenodo_doi.is_(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_fakenodo_synchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_fakenodo_doi.isnot(None),
                    DSMetaData.dataset_doi.is_(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_fakenodo_synchronized_dataset(self, dataset_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.is_(None), DataSet.id == dataset_id,
                    DSMetaData.staging_area.is_(False), DSMetaData.dataset_fakenodo_doi.isnot(None))
            .first()
        )

    def get_unsynchronized(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.is_(None),
                    DSMetaData.staging_area.is_(False), DSMetaData.dataset_fakenodo_doi.is_(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_unsynchronized_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.dataset_doi.is_(None), DataSet.id == dataset_id,
                    DSMetaData.staging_area.is_(False), DSMetaData.dataset_fakenodo_doi.is_(None))
            .first()
        )

    def get_staging_area(self, current_user_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DSMetaData.staging_area.is_(True))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def get_staging_area_dataset(self, current_user_id: int, dataset_id: int) -> DataSet:
        return (
            self.model.query.join(DSMetaData)
            .filter(DataSet.user_id == current_user_id, DataSet.id == dataset_id, DSMetaData.staging_area.is_(True))
            .order_by(self.model.created_at.desc())
            .first()
        )

    def count_synchronized_datasets(self):
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .count()
        )

    def count_unsynchronized_datasets(self):
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.is_(None), DSMetaData.dataset_fakenodo_doi.is_(None))
            .count()
        )

    def all_synchronized(self):
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .order_by(self.model.created_at.desc())
            .all()
        )

    def latest_synchronized(self):
        return (
            self.model.query.join(DSMetaData)
            .filter(DSMetaData.dataset_doi.isnot(None))
            .order_by(desc(self.model.id))
            .limit(5)
            .all()
        )

    def get_dataset_by_id(self, dataset_id: int) -> DataSet:
        return self.model.query.filter_by(id=dataset_id).first()

    def get_dataset_by_name(self, dataset_name: str) -> DataSet:
        return self.model.query.filter_by(name=dataset_name).first()

    def get_dataset_by_metadata_id(self, metadata_id):

        dataset = self.model.query.join(DSMetaData).filter(DSMetaData.id == metadata_id).first()
        return dataset


class DOIMappingRepository(BaseRepository):
    def __init__(self):
        super().__init__(DOIMapping)

    def get_new_doi(self, old_doi: str) -> str:
        return self.model.query.filter_by(dataset_doi_old=old_doi).first()


class DSRatingRepository(BaseRepository):
    def __init__(self):
        super().__init__(DSRating)

    def get_user_rating(self, ds_meta_data_id: int, user_id: int) -> Optional[DSRating]:
        return self.model.query.filter(DSRating.ds_meta_data_id == ds_meta_data_id, DSRating.user_id == user_id).first()

    def get_average_rating(self, ds_meta_data_id: int) -> float:
        average = self.model.query.filter(DSRating.ds_meta_data_id == ds_meta_data_id) \
            .with_entities(func.avg(DSRating.rating)).scalar()
        return average if average else 0.0

    def count_ratings(self, ds_meta_data_id: int) -> int:
        return self.model.query.filter(DSRating.ds_meta_data_id == ds_meta_data_id).count()
