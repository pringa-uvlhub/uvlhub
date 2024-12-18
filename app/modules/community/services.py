import logging
from datetime import datetime
from app.modules.community.models import Community
from app.modules.community.repositories import CommunityRepository
from core.services.BaseService import BaseService

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
                admin_by_id=current_user.id,
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

    def join_community(self, community_id, current_user):
        try:
            community = self.repository.get_by_id(community_id)
            if not community:
                raise ValueError(f"Community with ID {community_id} not found.")

            if community not in current_user.communities:
                current_user.communities.append(community)
                self.repository.session.commit()
                return True

            logger.info(f"User {current_user.id} is already a member of community {community_id}")
            return False

        except Exception as exc:
            logger.error(f"Error joining community: {exc}")
            self.repository.session.rollback()
            raise exc

    def leave_community(self, community_id: int, user) -> bool:
        community = self.repository.get_by_id(community_id)
        if not community:
            raise ValueError(f"Community with ID {community_id} not found.")

        if user not in community.users:
            raise ValueError("You are not a member of this community.")

        community.users.remove(user)
        self.repository.session.commit()
        return True

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

    def grant_admin_role(self, community_id, user, current_user):
        community = Community.query.get(community_id)
        if not community:
            raise ValueError("Community not found!")

        if not user:
            raise ValueError("User not found!")

        if user not in community.users:
            raise ValueError("User is not a member of the community!")

        if community.admin_by_id != current_user.id:
            raise ValueError("You are not authorized to assign an admin role!")

        community.admin_by_id = user.id
        self.repository.session.commit()

        return True

    def edit_community(self, community_id, form, current_user) -> Community:
        try:
            community = self.repository.get_by_id(community_id)
            if not community:
                raise ValueError(f"Community with ID {community_id} not found.")

            if community.admin_by_id != current_user.id:
                raise ValueError("You are not authorized to edit this community.")

            logger.info(f"Editing community with ID: {community_id} by user {current_user.id}")

            community.name = form.name.data
            community.description = form.description.data

            self.repository.session.commit()
            return community

        except Exception as exc:
            logger.error(f"Error editing community: {exc}")
            self.repository.session.rollback()
            raise exc

    def remove_user_from_community(self, community_id: int, user) -> bool:
        community = self.repository.get_by_id(community_id)

        if not community:
            raise ValueError(f"Community with ID {community_id} not found.")

        if user not in community.users:
            raise ValueError("User is not a member of this community.")

        community.users.remove(user)
        self.repository.session.commit()

        return True

    def filter_communities(self, query: str) -> list[Community]:
        try:
            # Búsqueda basada en el nombre o la descripción de la comunidad
            filtered_communities = (
                self.repository.model.query
                .filter(
                    (self.repository.model.name.ilike(f"%{query}%")) |
                    (self.repository.model.description.ilike(f"%{query}%"))
                )
                .order_by(self.repository.model.created_at.desc())
                .all()
            )
            return filtered_communities
        except Exception as exc:
            logger.error(f"Error filtering communities with query '{query}': {exc}")
            raise exc
