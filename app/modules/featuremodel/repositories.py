
from sqlalchemy import func
from app.modules.featuremodel.models import FMMetaData, FeatureModel
from core.repositories.BaseRepository import BaseRepository


class FeatureModelRepository(BaseRepository):
    def __init__(self):
        super().__init__(FeatureModel)

    def count_feature_models(self) -> int:
        max_id = self.model.query.with_entities(func.max(self.model.id)).scalar()
        return max_id if max_id is not None else 0

    def get_feature_model_by_id(self, feature_model_id: int):
        return self.model.query.filter_by(id=feature_model_id).first()


class FMMetaDataRepository(BaseRepository):
    def __init__(self):
        super().__init__(FMMetaData)