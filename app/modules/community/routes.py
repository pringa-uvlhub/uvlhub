import logging
from flask import request, render_template, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.modules.community.forms import CommunityForm
from app.modules.community.models import Community
from app.modules.auth.services import AuthenticationService
from app.modules.community.services import CommunityService
from app.modules.community import community_bp

community_service = CommunityService()
auth_service = AuthenticationService()
logger = logging.getLogger(__name__)


@community_bp.route('/community', methods=['GET'])
def index():
    communities = Community.query.all()
    return render_template('community/index.html', communities=communities)


@community_bp.route('/my_communities', methods=['GET'])
@login_required
def index_my_communities():
    # Filtra las comunidades que han sido creadas por el usuario actual
    communities = Community.query.filter_by(created_by_id=current_user.id).all()
    return render_template('community/index_my_communities.html', communities=communities)


@community_bp.route('/my_joined_communities', methods=['GET'])
@login_required
def index_joined_communities():

    communities = current_user.communities  # Suponiendo que tienes una relación Many-to-Many entre User y Community
    return render_template('community/index_joined_communities.html', communities=communities)


@community_bp.route('/community/create', methods=["GET", "POST"])
@login_required
def create():
    form = CommunityForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating community...")
            community_service = CommunityService()
            community = community_service.create_from_form(
                form=form,
                current_user=current_user
                )
            community_service.join_community(community.id, current_user)
            flash('Community created successfully!', 'success')
            return redirect(url_for('community.index_my_communities'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return jsonify({"message": str(e)}), 400

    return render_template('community/create.html', form=form)


@community_bp.route('/community/<int:community_id>', methods=['GET'])
def show_community(community_id):
    community = community_service.get_by_id(community_id)

    user = auth_service.get_by_id(community.created_by_id)

    user_fullname = f"{user.profile.name} {user.profile.surname}" if user.profile else "Unknown"

    if not community:
        flash('Community not found!', 'danger')
        return redirect(url_for('community.index'))
    return render_template('community/show.html', community=community, user_fullname=user_fullname)


@community_bp.route('/community/<int:community_id>/delete', methods=['POST'])
@login_required
def delete_community(community_id):
    community = community_service.get_by_id(community_id)
    if not community:
        flash('Community not found!', 'danger')
        return redirect(url_for('community.index'))

    if community.created_by_id != current_user.id:
        flash('You are not authorized to delete this community.', 'danger')
        return redirect(url_for('community.index'))

    try:
        if community_service.delete_community(community_id):
            flash('Community deleted successfully!', 'success')
        else:
            flash('Community could not be deleted.', 'danger')
    except Exception as e:
        flash(f'Error deleting community: {e}', 'danger')

    return redirect(url_for('community.index'))


@community_bp.route('/community/<int:community_id>/join', methods=['POST'])
@login_required
def join_community(community_id):
    try:
        success = community_service.join_community(community_id, current_user)

        if success:
            flash('You have successfully joined the community!', 'success')
        else:
            flash('You are already a member of this community.', 'info')

    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        flash('An error occurred while joining the community.', 'danger')

    return redirect(url_for('community.show_community', community_id=community_id))


@community_bp.route('/community/<int:community_id>/members', methods=['GET'])
def list_members(community_id):
    community = community_service.get_by_id(community_id)
    if not community:
        flash('Community not found!', 'danger')
        return redirect(url_for('community.index'))

    members = community.users
    return render_template('community/members.html', community=community, members=members)


@community_bp.route('/community/<int:community_id>/leave', methods=['POST'])
@login_required
def leave_community(community_id):
    try:
        success = community_service.leave_community(community_id, current_user)

        if success:
            flash('You have successfully left the community.', 'success')
        else:
            flash('You are not a member of this community.', 'info')

    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        flash('An error occurred while leaving the community.', 'danger')

    # Redirigir al show de la comunidad
    return redirect(url_for('community.show_community', community_id=community_id))

