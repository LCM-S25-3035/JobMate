from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length


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
