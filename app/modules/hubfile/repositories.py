from flask import abort
from sqlalchemy import func
from app.modules.auth.models import User
from app.modules.dataset.models import DataSet
from app.modules.featuremodel.models import FeatureModel
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
