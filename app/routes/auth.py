"""
User authentication routes
Handles registration, login, logout, and password management
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp
from app.models import db, User
from app.i18n import translate

logger = logging.getLogger(__name__)


def t(key, **kwargs):
    text = translate(key)
    return text.format(**kwargs) if kwargs else text


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


class RegistrationForm(FlaskForm):
    """User registration form with validation"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20),
        Regexp('^[A-Za-z0-9_]+$', message='Username must contain only letters, numbers, and underscores')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, field):
        """Check if username already exists"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken.')
    
    def validate_email(self, field):
        """Check if email already registered"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    """User login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('movie.home'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"New user registered: {user.username}")
            flash(t('flash.register_success'), 'success')
            return redirect(url_for('auth.login'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash(t('flash.register_error'), 'danger')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login route"""
    if current_user.is_authenticated:
        return redirect(url_for('movie.home'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash(t('flash.invalid_login'), 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=True)
        next_page = request.args.get('next')
        
        # Validate redirect URL for security
        if not next_page or next_page.startswith('/'):
            next_page = url_for('user.dashboard')
        
        flash(t('flash.welcome_back', username=user.username), 'success')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout route"""
    logout_user()
    flash(t('flash.logged_out'), 'info')
    return redirect(url_for('movie.home'))
