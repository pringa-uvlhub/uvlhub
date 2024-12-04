from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired,  Optional


class CommunityForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])

    # Logo field: Optional, but if provided, it must be an .svg file
    logo = FileField(
        "Image File",
        validators=[Optional()]
    )
    submit = SubmitField('Save community')

    def get_dsmetadata(self):

        return {
            "name": self.name.data,
            "description": self.description.data,
        }
