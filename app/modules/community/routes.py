from flask import app, request, render_template, flash, redirect, url_for, jsonify
from flask_login import current_user
from app import db
from app.modules.community.forms import CommunityForm
from app.modules.community.models import Community
from app.modules.community.repositories import CommunityRepository
from app.modules.community.services import CommunityService
from app.modules.community import community_bp
from werkzeug.utils import secure_filename
import os



community_service = CommunityService()


@community_bp.route('/community', methods=['GET'])
def index():
    communities = Community.query.all()
    return render_template('community/index.html', communities=communities)


@community_bp.route('/community/create', methods=['GET', 'POST'])
def create():
    form = CommunityForm()

    if request.method == 'POST':    

        if not form.validate_on_submit():
            return jsonify({"message": form.errors}), 400

        try:

            logo_filename = None
            if form.logo.data:
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

            flash('Community created successfully!', 'success')
            return redirect(url_for('community.index'))

        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'danger')
            return jsonify({"message": str(e)}), 400

    return render_template('community/create.html', form=form)
