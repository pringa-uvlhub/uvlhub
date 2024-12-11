import logging
from datetime import datetime
from app.modules.community.models import Community
from app.modules.community.repositories import CommunityRepository
from core.services.BaseService import BaseService

# Configurar el logger
logger = logging.getLogger(__name__)


class CommunityService(BaseService):
    def __init__(self):
        super().__init__(CommunityRepository())

    def create_from_form(self, form, current_user) -> Community:
        try:
            logger.info(f"Creating community with name: {form.name.data} by {current_user.id}")

            new_community = Community(
                name=form.name.data,
                description=form.description.data,
                created_at=datetime.utcnow(),
                created_by_id=current_user.id,
                logo=None
            )

            self.repository.session.add(new_community)

            self.repository.session.flush()

            self.repository.session.commit()
            return new_community

        except Exception as exc:
            logger.error(f"Error creating community: {exc}")
            self.repository.session.rollback()
            raise exc

    def get_all_communities(self):
        return self.repository.get_all()

    def get_community_by_name(self, name: str):
        return self.repository.get_community_by_name(name)

    def get_community_by_id(self, community_id: int):
        return self.repository.get_by_id(community_id)

    def delete_community(self, community_id: int) -> bool:
        community = self.repository.get_by_id(community_id)
        if not community:
            raise ValueError(f"Community with ID {community_id} not found.")
        return self.repository.delete_community(community_id)
