from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Optional, URL

class ProfileUpdateForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone', validators=[Optional()])
    city = StringField('City', validators=[Optional()])
    experience_level = SelectField('Experience Level', choices=[
        ('', 'Select experience level'),
        ('entry', 'Entry Level (0-2 years)'),
        ('junior', 'Junior (2-4 years)'),
        ('mid', 'Mid Level (4-7 years)'),
        ('senior', 'Senior Level (7+ years)'),
        ('executive', 'Executive')
    ], validators=[Optional()])
    bio = TextAreaField('Bio', validators=[Optional()])
    skills = TextAreaField('Skills', validators=[Optional()])

class SocialLinksForm(FlaskForm):
    linkedin_url = StringField('LinkedIn Profile', validators=[Optional(), URL()])
    github_url = StringField('GitHub Profile', validators=[Optional(), URL()])
    portfolio_url = StringField('Portfolio/Website', validators=[Optional(), URL()])
