
from sqlalchemy import func
from app.modules.featuremodel.models import FMMetaData, FeatureModel, FeatureModelRating
from core.repositories.BaseRepository import BaseRepository
from typing import Optional


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


class FeatureModelRatingRepository(BaseRepository):
    def __init__(self):
        super().__init__(FeatureModelRating)

    def get_user_rating(self, feature_model_id: int, user_id: int) -> Optional[FeatureModelRating]:
        return self.model.query.filter(FeatureModelRating.feature_model_id == feature_model_id,
                                       FeatureModelRating.user_id == user_id).first()

    def get_average_rating(self, feature_model_id: int) -> float:
        average = self.model.query.filter(FeatureModelRating.feature_model_id == feature_model_id) \
            .with_entities(func.avg(FeatureModelRating.rating)).scalar()
        return average if average else 0.0

    def count_ratings(self, feature_model_id: int) -> int:
        return self.model.query.filter(FeatureModelRating.feature_model_id == feature_model_id).count()
