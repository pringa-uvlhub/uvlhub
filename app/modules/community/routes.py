import logging
from flask import abort, request, render_template, flash, redirect, url_for, jsonify
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

    communities = current_user.communities
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
    if not community:
        abort(404)

    user = auth_service.get_by_id(community.created_by_id)

    user_admin = auth_service.get_by_id(community.admin_by_id)

    user_fullname = f"{user.profile.name} {user.profile.surname}" if user.profile else "Unknown"

    admin_fullname = f"{user_admin.profile.name} {user_admin.profile.surname}" if user.profile else "Unknown"

    if not community:
        flash('Community not found!', 'danger')
        return redirect(url_for('community.index'))
    return render_template('community/show.html', community=community, user_fullname=user_fullname,
                           admin_fullname=admin_fullname)


@community_bp.route('/community/<int:community_id>/delete', methods=['POST'])
@login_required
def delete_community(community_id):
    community = community_service.get_by_id(community_id)
    if not community:
        abort(404)

    if community.admin_by_id != current_user.id:
        abort(403)

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
        community = Community.query.get(community_id)

    # Si la comunidad no existe, abortar con un error 404
        if not community:
            abort(404, description="Community not found.")
        if current_user in community.users:
            abort(403, description="You are already a member of this community.")
        success = community_service.join_community(community_id, current_user)

        if success:
            flash('You have successfully joined the community!', 'success')
        else:
            abort(500)

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
        abort(404)

    members = community.users
    return render_template('community/members.html', community=community, members=members)


@community_bp.route('/community/<int:community_id>/leave', methods=['POST'])
@login_required
def leave_community(community_id):
    try:
        # Obtén la comunidad por ID
        community = community_service.get_by_id(community_id)

        if not community:
            abort(404)

        if community.admin_by_id == current_user.id and len(community.users.all()) == 1:
            flash(
                'You are the only member left in the community. Please delete the community instead of leaving.',
                'danger')
            return redirect(url_for('community.show_community', community_id=community_id))

        # Comprobar si el usuario es el admin y hay otros miembros
        if community.admin_by_id == current_user.id:
            flash(
                'You cannot leave the community because you are the admin. '
                'Please transfer the admin role to someone else first.',
                'danger')
            return redirect(url_for('community.show_community', community_id=community_id))

        # Si no es el administrador, procedemos con la salida
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


@community_bp.route('/community/<int:community_id>/grant_admin/<int:user_id>', methods=['POST'])
@login_required
def grant_admin(community_id, user_id):
    try:
        community = community_service.get_community_by_id(community_id)
        members = community.users
        user = auth_service.get_by_id(user_id)

        success = community_service.grant_admin_role(community_id, user, current_user)

        if success:
            flash('The user has been granted admin rights successfully.', 'success')
        else:
            flash('An error occurred while granting admin rights.', 'danger')

    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        flash('An error occurred while granting admin rights.', 'danger')

    return render_template('community/members.html', community=community, members=members)


@community_bp.route('/community/<int:community_id>/edit', methods=["GET", "POST"])
@login_required
def edit_community(community_id):
    community = community_service.get_community_by_id(community_id)

    if not community:
        abort(404)

    # Verificar que el usuario actual es el administrador
    if community.admin_by_id != current_user.id:
        abort(403)

    form = CommunityForm(obj=community)

    if request.method == 'POST':
        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            community_service.edit_community(community_id, form, current_user)
            flash('Community updated successfully!', 'success')
            return redirect(url_for('community.show_community', community_id=community_id))

        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            flash('An error occurred while updating the community.', 'danger')

    return render_template('community/edit.html', form=form, community=community)


@community_bp.route('/community/<int:community_id>/remove_user/<int:user_id>', methods=['POST'])
@login_required
def remove_user(community_id, user_id):
    try:
        # Obtener la comunidad y el usuario a expulsar
        community = community_service.get_by_id(community_id)
        user = auth_service.get_by_id(user_id)

        # Verificar si la comunidad existe
        if not community:
            flash('Community not found!', 'danger')
            return redirect(url_for('community.index'))

        # Verificar si el usuario es el administrador de la comunidad
        if community.admin_by_id != current_user.id:
            flash('You do not have permission to remove users from this community.', 'danger')
            return redirect(url_for('community.show_community', community_id=community_id))

        # Verificar si el usuario a expulsar es miembro de la comunidad
        if user not in community.users:
            flash('The user is not a member of this community.', 'info')
            return redirect(url_for('community.show_community', community_id=community_id))

        # Expulsar al usuario
        success = community_service.remove_user_from_community(community_id, user)

        if success:
            flash('The user has been removed from the community.', 'success')
        else:
            flash('An error occurred while removing the user.', 'danger')

    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        flash('An error occurred while removing the user.', 'danger')

    return redirect(url_for('community.show_community', community_id=community_id))


@community_bp.route('/communities', methods=['GET'])
def view_communities():
    search_term = request.args.get('search', '')
    if search_term:
        communities = Community.query.filter(Community.name.ilike(f'%{search_term}%')).all()
    else:
        communities = Community.query.all()
    return render_template('community/index.html', communities=communities)
