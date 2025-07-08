from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

class AutoApplySettingsForm(FlaskForm):
    """Form for configuring auto-apply settings."""
    enabled = BooleanField('Enable Auto-Apply')
    
    max_daily = IntegerField('Maximum Daily Applications', 
                            validators=[
                                DataRequired(), 
                                NumberRange(min=1, max=20, message="Please enter a number between 1 and 20")
                            ],
                            default=5)
    
    min_match_score = IntegerField('Minimum Match Score (%)', 
                                 validators=[
                                     DataRequired(), 
                                     NumberRange(min=50, max=100, message="Please enter a number between 50 and 100")
                                 ],
                                 default=80)
    
    cover_letter_type = SelectField('Cover Letter Generation', 
                                   choices=[
                                       ('none', 'No cover letter'),
                                       ('generic', 'Generic cover letter'),
                                       ('custom', 'Custom AI-generated cover letter per job')
                                   ],
                                   default='generic')
    
    preferred_job_types = SelectField('Preferred Job Types',
                                     choices=[
                                         ('all', 'All job types'),
                                         ('full_time', 'Full-time only'),
                                         ('remote', 'Remote only'),
                                         ('full_time_remote', 'Full-time remote only')
                                     ],
                                     default='all')
    
    submit = SubmitField('Save Settings')
