from app.modules.featuremodel.repositories import FMMetaDataRepository, FeatureModelRepository
from app.modules.hubfile.services import HubfileService
from core.services.BaseService import BaseService


class FeatureModelService(BaseService):
    def __init__(self):
        super().__init__(FeatureModelRepository())
        self.hubfile_service = HubfileService()
        self.repository = FeatureModelRepository()

    def total_feature_model_views(self) -> int:
        return self.hubfile_service.total_hubfile_views()

    def total_feature_model_downloads(self) -> int:
        return self.hubfile_service.total_hubfile_downloads()

    def count_feature_models(self):
        return self.repository.count_feature_models()
    
    def get_feature_model_by_id(self, feature_model_id: int):
        return self.repository.get_feature_model_by_id(feature_model_id)
    
    def feature_models_with_most_downloads(self):
        return self.repository.feature_models_with_most_downloads()

    class FMMetaDataService(BaseService):
        def __init__(self):
            super().__init__(FMMetaDataRepository())
