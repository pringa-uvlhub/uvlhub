from flask import render_template
from app.modules.community import community_bp


@community_bp.route('/community', methods=['GET'])
def index():
    return render_template('community/index.html')
