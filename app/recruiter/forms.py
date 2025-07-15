# app/recruiter/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from wtforms import SelectField
from wtforms.validators import DataRequired

class CreateJobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired()])
    company_name = StringField('Company Name', validators=[DataRequired()])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[Optional()])
    location = StringField('Location', validators=[DataRequired()])
    # Added fields for job category and skills
    job_category = StringField('Job Category', validators=[Optional()])  
    skills = StringField('Required Skills', validators=[Optional()])      

    salary_min = IntegerField('Min Salary', validators=[Optional(), NumberRange(min=0)])
    salary_max = IntegerField('Max Salary', validators=[Optional(), NumberRange(min=0)])

    employment_type = SelectField('Employment Type', choices=[
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('internship', 'Internship')
    ], validators=[DataRequired()])

    work_setting = SelectField('Work Setting', choices=[
        ('office', 'Office'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    

    experience_level = SelectField('Experience Level', choices=[
        ('junior', 'Junior'),
        ('mid', 'Mid'),
        ('senior', 'Senior')
    ], validators=[DataRequired()])

    submit = SubmitField('Post Job')
