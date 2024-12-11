from flask import abort
from sqlalchemy import func
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet
from app.modules.featuremodel.models import FeatureModel
from app.modules.featuremodel.repositories import FeatureModelRepository
from app.modules.hubfile.models import Hubfile, HubfileDownloadRecord, HubfileViewRecord
from core.repositories.BaseRepository import BaseRepository
from app import db


class HubfileRepository(BaseRepository):
    def __init__(self):
        super().__init__(Hubfile)

    def get_owner_user_by_hubfile(self, hubfile: Hubfile) -> User:
        return (
            db.session.query(User)
            .join(DataSet)
            .join(FeatureModel)
            .join(Hubfile)
            .filter(Hubfile.id == hubfile.id)
            .first()
        )

    def get_dataset_by_hubfile(self, hubfile: Hubfile) -> DataSet:
        return db.session.query(DataSet).join(FeatureModel).join(Hubfile).filter(Hubfile.id == hubfile.id).first()

    def get_featureModels_by_hubfile_id(id: int) -> DataSet:
        return db.session.query(FeatureModel).join(FeatureModel).join(Hubfile).filter(Hubfile.id == id).first()

    def get_hubfile_by_name(file_name: str):
        hubfile = Hubfile.query.filter_by(name=file_name).first()
        if hubfile is None:
            abort(404, description=f'Hubfile with name "{file_name}" not found')
        return hubfile


class HubfileViewRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(HubfileViewRecord)

    def total_hubfile_views(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0


class HubfileDownloadRecordRepository(BaseRepository):
    def __init__(self):
        super().__init__(HubfileDownloadRecord)

    def total_hubfile_downloads(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def feature_models_with_most_downloads(self):
        download_count = {}
        for download in self.model.query.all():
            file_id = download.file_id
            hubfile = Hubfile.query.get(file_id)
            feature_model_id = hubfile.feature_model_id
            if feature_model_id in download_count:
                download_count[feature_model_id] += 1
            else:
                download_count[feature_model_id] = 1
    
        most_downloaded_feature_models = sorted(download_count.items(), key=lambda x: x[1], reverse=True)[:5]
        feature_model_names = []
        download_counts = []
    
        for feature_model_id, count in most_downloaded_feature_models:
            feature_model_repo = FeatureModelRepository()
            feature_model = feature_model_repo.get_feature_model_by_id(feature_model_id)
            feature_model_names.append(feature_model.fm_meta_data.title)  # Asegúrate de que `feature_model` tenga un atributo `fm_meta_data` con `title`
            download_counts.append(count)
    
        return feature_model_names, download_counts
