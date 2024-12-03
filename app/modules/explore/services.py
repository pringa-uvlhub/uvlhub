from app.modules.explore.repositories import ExploreRepository
from core.services.BaseService import BaseService


class ExploreService(BaseService):
    def __init__(self):
        super().__init__(ExploreRepository())

    def filter(self, query="", queryAuthor="", queryTag="", queryFeatures="", queryModels="", sorting="newest",
               publication_type="any", tags=[], **kwargs):
        return self.repository.filter(query, queryAuthor, queryTag, queryFeatures, queryModels, sorting,
                                      publication_type, tags, **kwargs)
