<<<<<<< Updated upstream
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
=======
"""
Forms for recruiter functionality
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError

class CreateJobForm(FlaskForm):
    """Form for creating a new job posting"""
    
    # Basic Information
    title = StringField('Job Title', validators=[
        DataRequired(message='Job title is required'),
        Length(min=3, max=200, message='Job title must be between 3 and 200 characters')
    ])
    
    company_name = StringField('Company Name', validators=[
        DataRequired(message='Company name is required'),
        Length(min=2, max=100, message='Company name must be between 2 and 100 characters')
    ])
    
    location = StringField('Location', validators=[
        DataRequired(message='Location is required'),
        Length(min=2, max=100, message='Location must be between 2 and 100 characters')
    ])
    
    job_category = SelectField('Job Category', choices=[
        ('', 'Select Department'),
        ('engineering', 'Engineering'),
        ('marketing', 'Marketing'),
        ('sales', 'Sales'),
        ('product', 'Product'),
        ('design', 'Design'),
        ('data', 'Data & Analytics'),
        ('operations', 'Operations'),
        ('hr', 'Human Resources'),
        ('finance', 'Finance'),
        ('other', 'Other')
    ], validators=[Optional()])
    
    # Job Details
    description = TextAreaField('Job Description', validators=[
        DataRequired(message='Job description is required'),
        Length(min=50, message='Job description must be at least 50 characters')
    ])
    
    requirements = TextAreaField('Requirements', validators=[
        DataRequired(message='Requirements are required'),
        Length(min=20, message='Requirements must be at least 20 characters')
    ])
    
    # Employment Details
    employment_type = SelectField('Employment Type', choices=[
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship')
    ], validators=[DataRequired()])
    
    remote_type = SelectField('Remote Type', choices=[
        ('onsite', 'Onsite'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    
    experience_level = SelectField('Experience Level', choices=[
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive')
    ], validators=[DataRequired()])
    
    # Salary (optional)
    salary_min = IntegerField('Minimum Salary', validators=[
        Optional(),
        NumberRange(min=0, message='Salary must be positive')
    ])
    
    salary_max = IntegerField('Maximum Salary', validators=[
        Optional(),
        NumberRange(min=0, message='Salary must be positive')
    ])
    
    # Additional fields
    benefits = TextAreaField('Benefits', validators=[Optional()])
    skills = StringField('Skills Required', validators=[Optional()])
    
    # Submit button
    submit = SubmitField('Create Job Posting')
    
    def validate_salary_max(self, field):
        """Custom validator to ensure salary_max >= salary_min"""
        if field.data and self.salary_min.data:
            if field.data < self.salary_min.data:
                raise ValidationError('Maximum salary must be greater than or equal to minimum salary')
>>>>>>> Stashed changes
