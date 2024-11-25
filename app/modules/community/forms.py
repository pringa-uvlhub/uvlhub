from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Regexp, Optional

class CommunityForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    
    # Logo field: Optional, but if provided, it must be an .svg file
    logo = FileField(
        "Image File", 
        validators=[Optional()]
    )
    submit = SubmitField('Save community')
