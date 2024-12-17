import logging
from flask import render_template
from app.modules.featuremodel import featuremodel_bp
from flask_login import login_required, current_user
from flask import (
    request,
    jsonify,
)
from app.modules.featuremodel.services import (
    FeatureModelService,
    FeatureModelRatingService
)

logger = logging.getLogger(__name__)

featuremodel_service = FeatureModelService()
featuremodelrating_service = FeatureModelRatingService()


@featuremodel_bp.route('/featuremodel', methods=['GET'])
def index():
    return render_template('featuremodel/index.html')


@featuremodel_bp.route("/feature-models/<int:feature_model_id>/rate", methods=["POST"])
@login_required
def rate_feature_model(feature_model_id):
    user_id = current_user.id

    try:
        rating_value = float(request.json.get('rating'))

        if not (0 <= rating_value <= 5) or rating_value != rating_value \
                or not float('-inf') < rating_value < float('inf'):
            raise ValueError
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid rating value. Must be a finite number between 0 and 5.'}), 400

    rating = featuremodelrating_service.add_or_update_rating(feature_model_id, user_id, rating_value)
    return jsonify({'message': 'Rating added', 'rating': rating.to_dict()}), 200


@featuremodel_bp.route('/feature-models/<int:feature_model_id>/average-rating', methods=['GET'])
def get_feature_model_average_rating(feature_model_id):
    featuremodel = featuremodel_service.get_or_404(feature_model_id)
    average_rating = featuremodelrating_service.get_dataset_average_rating(featuremodel.id)
    return jsonify({'average_rating': average_rating}), 200
