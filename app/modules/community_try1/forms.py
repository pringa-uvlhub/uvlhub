from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, FieldList, FormField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, URL, Optional


class AuthorForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    affiliation = StringField("Affiliation")
    orcid = StringField("ORCID")
    gnd = StringField("GND")

    class Meta:
        csrf = False  # disable CSRF because is subform

    def get_author(self):
        return {
            "name": self.name.data,
            "affiliation": self.affiliation.data,
            "orcid": self.orcid.data,
        }


class CommunityForm(FlaskForm):
    name = StringField("Community Name", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    visibility = SelectField(
        "Visibility",
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('restricted', 'Restricted')
        ],
        validators=[DataRequired()],
    )
    community_doi = StringField("Community DOI", validators=[Optional(), URL()])
    tags = StringField("Tags (separated by commas)")
    moderators = FieldList(FormField(AuthorForm), min_entries=1)  # Assuming AuthorForm is used for moderator details

    submit = SubmitField("Create Community")

    def get_community_metadata(self):
        return {
            "name": self.name.data,
            "description": self.description.data,
            
        }

    def get_moderators(self):
        return [moderator.get_author() for moderator in self.moderators]
    
    