import logging
from flask import request, render_template, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from app.modules.community.forms import CommunityForm
from app.modules.community.models import Community
from app.modules.auth.services import AuthenticationService
from app.modules.community.services import CommunityService
from app.modules.community import community_bp
from werkzeug.utils import secure_filename
import os

community_service = CommunityService()
auth_service = AuthenticationService()
logger = logging.getLogger(__name__)


@community_bp.route('/community', methods=['GET'])
def index():
    communities = Community.query.all()
    return render_template('community/index.html', communities=communities)


@community_bp.route('/community/create', methods=["GET", "POST"])
@login_required
def create():
    form = CommunityForm()

    if request.method == 'POST':
        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:
            logger.info("Creating community...")

            logo_filename = None
            if form.logo.data:
                logger.info("1111111111")
                logo_file = form.logo.data
                logo_filename = secure_filename(logo_file.filename)

                upload_folder = os.path.join('app/static/img/community')
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)

                file_path = os.path.join(upload_folder, logo_filename)
                logo_file.save(file_path)

                community_service = CommunityService()
                community_service.create_from_form(
                    form=form,
                    current_user=current_user,
                    logo_filename=logo_filename)
            else:
                community_service = CommunityService()
                community_service.create_from_form(
                    form=form,
                    current_user=current_user
                    )
            flash('Community created successfully!', 'success')
            return redirect(url_for('community.index'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return jsonify({"message": str(e)}), 400

    return render_template('community/create.html', form=form)


@community_bp.route('/community/<int:id>', methods=['GET'])
def show_community(community_id):
    community = community_service.get_by_id(community_id)

    user = auth_service.get_by_id(community.created_by_id)

    user_fullname = f"{user.profile.name} {user.profile.surname}" if user.profile else "Unknown"

    if not community:
        flash('Community not found!', 'danger')
        return redirect(url_for('community.index'))
    return render_template('community/show.html', community=community, user_fullname=user_fullname)


@community_bp.route('/community/<int:id>/delete', methods=['POST'])
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
