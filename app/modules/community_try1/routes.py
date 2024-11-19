import logging

from app.modules.dataset import dataset_bp
from flask import (
    redirect,
    render_template,
    request,
    jsonify,
    send_from_directory,
    make_response,
    abort,
    url_for,
)
from app.modules.community.forms import CommunityForm
from flask_login import login_required, current_user
from app.modules.community.services import (
    CommunitiesService
)
communities_service = CommunitiesService()
logger = logging.getLogger(__name__)


@dataset_bp.route("/community/create", methods=["GET", "POST"])
@login_required
def create_community():
    form = CommunityForm()
    if request.method == "POST":

        community = None

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating community...")
            community = communities_service.create_from_form(form=form, current_user=current_user)
            logger.info(f"Created community: {community}")
        except Exception as exc:
            logger.exception(f"Exception while creating community: {exc}")
            return jsonify({"Exception while creating community: ": str(exc)}), 400

        msg = "Community created successfully!"
        return jsonify({"message": msg, "community_id": community.id}), 201

    return render_template("dataset/create_community.html", form=form)


@dataset_bp.route('/community/list', methods=['GET'])
def list_communities():
    limit = request.args.get('limit', default=10, type=int)
    try:
        communities = communities_service.list_communities(limit=limit)
        return jsonify([community.to_dict() for community in communities]), 200
    except Exception as exc:
        logger.exception(f"Error listing communities: {exc}")
        return jsonify({'error': str(exc)}), 500


@dataset_bp.route('/community/update/<int:community_id>', methods=['PUT'])
@login_required
def update_community_description(community_id):
    data = request.get_json()
    new_description = data.get('description')

    if not new_description:
        return jsonify({'error': 'Description is required'}), 400

    try:
        community = communities_service.update_community_description(community_id, new_description)
        if not community:
            return jsonify({'error': 'Community not found'}), 404
        return jsonify({'message': 'Community updated successfully', 'community': community.to_dict()}), 200
    except Exception as exc:
        logger.exception(f"Error updating community: {exc}")
        return jsonify({'error': str(exc)}), 500


@dataset_bp.route('/community/delete/<int:community_id>', methods=['DELETE'])
@login_required
def delete_community(community_id):
    try:
        communities_service.delete_community(community_id)
        return jsonify({'message': 'Community deleted successfully'}), 200
    except Exception as exc:
        logger.exception(f"Error deleting community: {exc}")
        return jsonify({'error': str(exc)}), 500
