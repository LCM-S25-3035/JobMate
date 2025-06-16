"""
Authentication Routes for JobMate
Handles login, registration, logout, and email verification
"""

from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse as url_parse
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm
from app.models.user import User
from app import db
import secrets


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Find user by email
        user = User.find_by_email(form.email.data)
        
        # Check credentials
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Log in user
            login_user(user, remember=form.remember_me.data)
            user.update_last_login()
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if user.is_applicant():
                    next_page = url_for('main.applicant_dashboard')
                else:  # recruiter
                    next_page = url_for('main.recruiter_dashboard')
            
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User.create_user(
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                user_type=form.user_type.data
            )
            
            # Generate verification token
            user.verification_token = secrets.token_urlsafe(32)
            db.session.commit()
            
            # TODO: Send verification email
            
            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))
            
        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/verify-email/<token>')
def verify_email(token):
    """Email verification route"""
    user = User.query.filter_by(verification_token=token).first()
    
    if not user:
        flash('Invalid or expired verification link.', 'error')
        return redirect(url_for('auth.login'))
    
    if user.is_verified:
        flash('Email already verified.', 'info')
        return redirect(url_for('auth.login'))
    
    user.is_verified = True
    user.verification_token = None
    db.session.commit()
    
    flash('Email verified successfully! You can now log in.', 'success')
    return redirect(url_for('auth.login'))


@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Password reset request route"""
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ResetPasswordRequestForm()
    
    if form.validate_on_submit():
        user = User.find_by_email(form.email.data)
        if user:
            # TODO: Send password reset email
            pass
        
        # Always show success message for security
        flash('Check your email for instructions to reset your password.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', 
                         title='Reset Password', form=form)


@bp.route('/user-profile')
@login_required
def user_profile():
    """Get current user profile (API endpoint)"""
    return jsonify(current_user.to_dict())


@bp.route('/check-email')
def check_email():
    """Check if email is already registered (API endpoint)"""
    email = request.args.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'exists': False, 'message': 'Email required'})
    
    user = User.find_by_email(email)
    return jsonify({
        'exists': user is not None,
        'message': 'Email already registered' if user else 'Email available'
    })


# API Routes for frontend integration
@bp.route('/api/login', methods=['POST'])
def api_login():
    """API login endpoint for AJAX requests"""
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    user = User.find_by_email(data['email'])
    
    if user and user.check_password(data['password']):
        if not user.is_active:
            return jsonify({'success': False, 'message': 'Account deactivated'}), 403
        
        login_user(user, remember=data.get('remember', False))
        user.update_last_login()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user.to_dict(),
            'redirect_url': url_for('main.applicant_dashboard' if user.is_applicant() 
                                  else 'main.recruiter_dashboard')
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401


@bp.route('/api/register', methods=['POST'])
def api_register():
    """API registration endpoint for AJAX requests"""
    data = request.get_json()
    
    required_fields = ['email', 'password', 'first_name', 'last_name', 'user_type']
    if not data or not all(field in data for field in required_fields):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    try:
        user = User.create_user(
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            user_type=data['user_type']
        )
        
        user.verification_token = secrets.token_urlsafe(32)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please verify your email.',
            'user_id': user.id
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Registration failed'}), 500 