from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app.modules.admin import admin_bp


@admin_bp.route('/admin', methods=['GET'])
def index():
    return render_template('admin/index.html')


@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('public.index'))
    return render_template('admin/dashboard.html')
