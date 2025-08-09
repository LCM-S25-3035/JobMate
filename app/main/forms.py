from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional, URL


class JobApplicationForm(FlaskForm):
    """Form for job applications"""
    cover_letter = TextAreaField('Cover Letter', 
                                validators=[DataRequired(), Length(min=50, max=2000)],
                                render_kw={'rows': 6, 'placeholder': 'Tell the employer why you\'re interested in this position and what makes you a great fit...'})
    
    additional_notes = TextAreaField('Additional Information', 
                                   validators=[Length(max=500)],
                                   render_kw={'rows': 3, 'placeholder': 'Any additional information you\'d like to share (availability, salary expectations, etc.)...'})
    
    resume_file = FileField('Resume/CV', 
                           validators=[FileAllowed(['pdf', 'doc', 'docx'], 'Please upload PDF or Word documents only.')])
    
    consent = BooleanField('Data Processing Consent', validators=[DataRequired()])
    
    submit = SubmitField('Submit Application')


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
