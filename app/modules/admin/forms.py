from flask_wtf import FlaskForm
from wtforms import SubmitField


class AdminForm(FlaskForm):
    submit = SubmitField('Save admin')
