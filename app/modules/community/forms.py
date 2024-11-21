from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, validators, FileField
from wtforms.validators import DataRequired


class CommunityForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    logo = FileField(u'Image File', [validators.regexp(u'^[^/\\]\.jpg$')])
    submit = SubmitField('Save community')
