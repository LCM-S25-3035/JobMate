"""
Search Forms for JobMate
Forms for job search and filtering
"""

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, BooleanField, SelectMultipleField, DecimalField
from wtforms.validators import Optional, NumberRange
from wtforms.widgets import TextArea


class JobSearchForm(FlaskForm):
    """Main job search form"""
    
    # Search query
    query = StringField('Search Jobs', validators=[Optional()])
    
    # Location filters
    location = StringField('Location', validators=[Optional()])
    remote_type = SelectField('Remote Type', choices=[
        ('', 'Any'),
        ('onsite', 'On-site'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid')
    ], validators=[Optional()])
    
    # Employment filters
    employment_type = SelectField('Employment Type', choices=[
        ('', 'Any'),
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('co_op', 'Co-op')
    ], validators=[Optional()])
    
    experience_level = SelectField('Experience Level', choices=[
        ('', 'Any'),
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('executive', 'Executive')
    ], validators=[Optional()])
    
    # Salary filters
    salary_min = IntegerField('Minimum Salary', validators=[Optional(), NumberRange(min=0)])
    salary_max = IntegerField('Maximum Salary', validators=[Optional(), NumberRange(min=0)])
    
    # Company filters
    company_size = SelectField('Company Size', choices=[
        ('', 'Any'),
        ('startup', 'Startup'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('enterprise', 'Enterprise')
    ], validators=[Optional()])
    
    industry = StringField('Industry', validators=[Optional()])
    
    # Skills filter
    skills = StringField('Required Skills', validators=[Optional()])
    
    # Special filters
    featured_only = BooleanField('Featured Jobs Only')
    urgent_only = BooleanField('Urgent Jobs Only')
    
    # Sorting
    sort_by = SelectField('Sort By', choices=[
        ('relevance', 'Relevance'),
        ('date', 'Newest First'),
        ('salary', 'Highest Salary'),
        ('featured', 'Featured First'),
        ('applications', 'Most Applications'),
        ('views', 'Most Views')
    ], default='relevance', validators=[Optional()])
    
    # Pagination
    page = IntegerField('Page', default=1, validators=[Optional(), NumberRange(min=1)])
    per_page = SelectField('Jobs per Page', choices=[
        ('10', '10'),
        ('20', '20'),
        ('50', '50'),
        ('100', '100')
    ], default='20', validators=[Optional()])


class AdvancedJobSearchForm(JobSearchForm):
    """Advanced job search form with additional filters"""
    
    # Additional employment details
    min_experience_years = IntegerField('Min Experience (Years)', validators=[Optional(), NumberRange(min=0)])
    max_experience_years = IntegerField('Max Experience (Years)', validators=[Optional(), NumberRange(min=0)])
    
    # Company type
    company_type = SelectField('Company Type', choices=[
        ('', 'Any'),
        ('public', 'Public'),
        ('private', 'Private'),
        ('nonprofit', 'Non-profit'),
        ('government', 'Government'),
        ('startup', 'Startup')
    ], validators=[Optional()])
    
    # Date filters
    posted_since = SelectField('Posted Since', choices=[
        ('', 'Any time'),
        ('1', 'Last 24 hours'),
        ('7', 'Last week'),
        ('30', 'Last month'),
        ('90', 'Last 3 months')
    ], validators=[Optional()])
    
    # Source filter
    source = SelectField('Job Source', choices=[
        ('', 'Any'),
        ('internal', 'Internal'),
        ('linkedin', 'LinkedIn'),
        ('indeed', 'Indeed'),
        ('glassdoor', 'Glassdoor'),
        ('workopolis', 'Workopolis'),
        ('monster', 'Monster'),
        ('other', 'Other')
    ], validators=[Optional()])


class QuickSearchForm(FlaskForm):
    """Quick search form for header/navbar"""
    
    q = StringField('Search jobs, companies, skills...', validators=[Optional()])
    location = StringField('Location', validators=[Optional()])


class AutocompleteForm(FlaskForm):
    """Form for autocomplete suggestions"""
    
    query = StringField('Query', validators=[Optional()])
    limit = IntegerField('Limit', default=5, validators=[Optional(), NumberRange(min=1, max=20)])


class FilterForm(FlaskForm):
    """Form for applying filters without search query"""
    
    # Location
    locations = SelectMultipleField('Locations', choices=[], validators=[Optional()])
    
    # Remote work
    remote_types = SelectMultipleField('Remote Types', choices=[
        ('onsite', 'On-site'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid')
    ], validators=[Optional()])
    
    # Employment
    employment_types = SelectMultipleField('Employment Types', choices=[
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('co_op', 'Co-op')
    ], validators=[Optional()])
    
    # Experience
    experience_levels = SelectMultipleField('Experience Levels', choices=[
        ('entry', 'Entry Level'),
        ('junior', 'Junior'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior'),
        ('lead', 'Lead'),
        ('executive', 'Executive')
    ], validators=[Optional()])
    
    # Company
    company_sizes = SelectMultipleField('Company Sizes', choices=[
        ('startup', 'Startup'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('enterprise', 'Enterprise')
    ], validators=[Optional()])
    
    # Industries
    industries = SelectMultipleField('Industries', choices=[], validators=[Optional()])
    
    # Skills
    required_skills = SelectMultipleField('Required Skills', choices=[], validators=[Optional()])
    
    # Salary range
    salary_min = IntegerField('Minimum Salary', validators=[Optional(), NumberRange(min=0)])
    salary_max = IntegerField('Maximum Salary', validators=[Optional(), NumberRange(min=0)])


class SavedSearchForm(FlaskForm):
    """Form for saving search criteria"""
    
    name = StringField('Search Name', validators=[Optional()])
    query = StringField('Query', validators=[Optional()])
    filters = StringField('Filters (JSON)', widget=TextArea(), validators=[Optional()])
    email_notifications = BooleanField('Email Notifications', default=True)
    frequency = SelectField('Notification Frequency', choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly')
    ], default='weekly', validators=[Optional()])


def get_dynamic_choices(facets):
    """Convert facet data to form choices"""
    choices = []
    
    for facet in facets:
        if isinstance(facet, dict) and 'key' in facet and 'count' in facet:
            label = f"{facet['key']} ({facet['count']})"
            choices.append((facet['key'], label))
    
    return choices


def populate_filter_choices(form, facets):
    """Populate filter form with dynamic choices from facets"""
    
    if 'locations' in facets:
        form.locations.choices = get_dynamic_choices(facets['locations'])
    
    if 'industries' in facets:
        form.industries.choices = get_dynamic_choices(facets['industries'])
    
    if 'required_skills' in facets:
        form.required_skills.choices = get_dynamic_choices(facets['required_skills'])
    
    return form 