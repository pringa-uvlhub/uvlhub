import logging

from typing import Optional

from app.modules.community.repositories import (

    CommunitiesRepository
)


from core.services.BaseService import BaseService

logger = logging.getLogger(__name__)


class CommunitiesService(BaseService):
    def __init__(self):
        super().__init__(CommunitiesRepository())

    def get_all_communities(self):
        return self.repository.get_all()
    
    def get_community_by_name(self, name: str):
        return self.repository.get_community_by_name(name)

    def list_communities(self, limit: int = 10):
        return self.repository.list_communities(limit=limit)
    
    def get_community_by_id(self, community_id: int):
        return self.repository.get_by_id(community_id)

    def create_community(self, name: str, description: Optional[str] = None):
        try:
            community = self.repository.create(name=name, description=description)
            self.repository.session.commit()
            return community
        except Exception as exc:
            logger.error(f"Error creando comunidad: {exc}")
            self.repository.session.rollback()
            raise exc

    def update_community_description(self, community_id: int, new_description: str):
        try:
            community = self.repository.update_community_description(community_id, new_description)
            self.repository.session.commit()
            return community
        except Exception as exc:
            logger.error(f"Error actualizando descripción de la comunidad con ID {community_id}: {exc}")
            self.repository.session.rollback()
            raise exc
        
    def delete_community(self, community_id: int):
        try:
            self.repository.delete_community(community_id)
            self.repository.session.commit()
        except Exception as exc:
            logger.error(f"Error eliminando comunidad con ID {community_id}: {exc}")
            self.repository.session.rollback()
            raise exc
        