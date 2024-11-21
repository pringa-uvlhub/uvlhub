from flask import render_template
from app.modules.community import community_bp
from app.modules.community.models import Community


@community_bp.route('/community', methods=['GET'])
def index():
    communities = Community.query.all()
    return render_template('community/index.html', communities=communities)
