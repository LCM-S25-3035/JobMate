"""
Authentication Forms for JobMate
WTForms for login, registration, and password management
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import User


class LoginForm(FlaskForm):
    """Login form for user authentication"""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ], render_kw={'placeholder': 'Enter your email', 'class': 'form-control'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required')
    ], render_kw={'placeholder': 'Enter your password', 'class': 'form-control'})
    
    remember_me = BooleanField('Remember Me', render_kw={'class': 'form-check-input'})
    
    submit = SubmitField('Sign In', render_kw={'class': 'btn btn-primary'})


class RegistrationForm(FlaskForm):
    """Registration form for new users"""
    
    first_name = StringField('First Name', validators=[
        DataRequired(message='First name is required'),
        Length(min=2, max=50, message='First name must be between 2 and 50 characters')
    ], render_kw={'placeholder': 'Enter your first name', 'class': 'form-control'})
    
    last_name = StringField('Last Name', validators=[
        DataRequired(message='Last name is required'),
        Length(min=2, max=50, message='Last name must be between 2 and 50 characters')
    ], render_kw={'placeholder': 'Enter your last name', 'class': 'form-control'})
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ], render_kw={'placeholder': 'Enter your email', 'class': 'form-control'})
    
    user_type = SelectField('I am a...', validators=[
        DataRequired(message='Please select your role')
    ], choices=[
        ('applicant', 'Job Seeker'),
        ('recruiter', 'Recruiter/Employer')
    ], render_kw={'class': 'form-select'})
    
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'placeholder': 'Create a strong password', 'class': 'form-control'})
    
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm your password', 'class': 'form-control'})
    
    terms_accepted = BooleanField('I agree to the Terms of Service and Privacy Policy', 
                                validators=[DataRequired(message='You must accept the terms')],
                                render_kw={'class': 'form-check-input'})
    
    submit = SubmitField('Create Account', render_kw={'class': 'btn btn-primary'})
    
    def validate_email(self, email):
        """Check if email is already registered"""
        user = User.find_by_email(email.data)
        if user:
            raise ValidationError('This email is already registered. Please use a different email or try logging in.')
    
    def validate_password(self, password):
        """Validate password strength"""
        password_str = password.data
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password_str):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password_str):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        # Check for at least one digit
        if not any(c.isdigit() for c in password_str):
            raise ValidationError('Password must contain at least one number.')


class ResetPasswordRequestForm(FlaskForm):
    """Form to request password reset"""
    
    email = StringField('Email', validators=[
        DataRequired(message='Email is required'),
        Email(message='Invalid email address')
    ], render_kw={'placeholder': 'Enter your registered email', 'class': 'form-control'})
    
    submit = SubmitField('Send Reset Link', render_kw={'class': 'btn btn-primary'})


class ResetPasswordForm(FlaskForm):
    """Form to reset password with token"""
    
    password = PasswordField('New Password', validators=[
        DataRequired(message='Password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'placeholder': 'Enter new password', 'class': 'form-control'})
    
    password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your password'),
        EqualTo('password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm new password', 'class': 'form-control'})
    
    submit = SubmitField('Reset Password', render_kw={'class': 'btn btn-primary'})
    
    def validate_password(self, password):
        """Validate password strength"""
        password_str = password.data
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password_str):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password_str):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        # Check for at least one digit
        if not any(c.isdigit() for c in password_str):
            raise ValidationError('Password must contain at least one number.')


class ChangePasswordForm(FlaskForm):
    """Form to change password when logged in"""
    
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required')
    ], render_kw={'placeholder': 'Enter current password', 'class': 'form-control'})
    
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required'),
        Length(min=8, message='Password must be at least 8 characters long')
    ], render_kw={'placeholder': 'Enter new password', 'class': 'form-control'})
    
    new_password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password'),
        EqualTo('new_password', message='Passwords must match')
    ], render_kw={'placeholder': 'Confirm new password', 'class': 'form-control'})
    
    submit = SubmitField('Change Password', render_kw={'class': 'btn btn-primary'})
    
    def validate_new_password(self, new_password):
        """Validate new password strength"""
        password_str = new_password.data
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password_str):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password_str):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        # Check for at least one digit
        if not any(c.isdigit() for c in password_str):
            raise ValidationError('Password must contain at least one number.') 