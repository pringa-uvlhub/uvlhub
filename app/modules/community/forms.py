from flask_wtf import FlaskForm
from wtforms import SubmitField


class CommunityForm(FlaskForm):
    submit = SubmitField('Save community')
