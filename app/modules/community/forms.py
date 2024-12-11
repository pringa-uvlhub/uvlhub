from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class CommunityForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])

    # Logo field: Optional, but if provided, it must be an .svg file

    submit = SubmitField('Save community')

    def get_dsmetadata(self):

        return {
            "name": self.name.data,
            "description": self.description.data,
        }
