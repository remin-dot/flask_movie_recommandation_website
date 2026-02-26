"""
Flask application factory and initialization
Sets up database, login manager, blueprints, and error handlers
"""

from flask import Flask, render_template, jsonify, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from config import get_config
from app.models import db, User
from app.i18n import SUPPORTED_LANGUAGES, get_current_language, localize_text, translate
from app.services.posters import ensure_movie_schema, sync_movie_posters, remove_duplicate_movies
from app.utils import setup_logging
import logging


def create_app(config_name='development'):
    """
    Application factory function
    Creates and configures Flask app instance
    
    Args:
        config_name: Configuration environment ('development', 'testing', 'production')
    
    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Setup logging
    setup_logging(app)
    logger = logging.getLogger(__name__)
    logger.info(f"Creating Flask app in {config_name} environment")
    
    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return db.session.get(User, int(user_id))
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.movie import movie_bp
    from app.routes.user import user_bp
    from app.routes.admin import admin_bp
    from app.routes.locale import locale_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(movie_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(locale_bp)
    
    # Register error handlers
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 - Bad request"""
        app.logger.warning(f"Bad request: {error}")
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(403)
    def forbidden_error(error):
        """Handle 403 - Forbidden access"""
        app.logger.warning(f"Forbidden access: {error}")
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 - Page not found"""
        app.logger.warning(f"Page not found: {error}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 - Internal server error"""
        app.logger.error(f"Internal server error: {error}", exc_info=True)
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unexpected exceptions"""
        app.logger.error(f"Unhandled exception: {error}", exc_info=True)
        db.session.rollback()
        
        # Return JSON for API requests
        if request.content_type and 'application/json' in request.content_type:
            return jsonify({
                'error': 'An unexpected error occurred',
                'status': 500
            }), 500
        
        return render_template('errors/500.html'), 500
    
    # Register context processor
    @app.context_processor
    def inject_user():
        """Make current_user available in all templates"""
        from flask_login import current_user
        return dict(current_user=current_user)

    @app.context_processor
    def inject_i18n():
        """Provide translation helpers to templates."""
        return {
            't': translate,
            'current_lang': get_current_language(),
            'supported_languages': SUPPORTED_LANGUAGES,
            'localize_text': localize_text,
        }
    
    # Database initialization commands
    with app.app_context():
        db.create_all()
        ensure_movie_schema()
        remove_duplicate_movies()
        # normalize titles/years and strip HTML from stored data
        from app.services.posters import clean_movie_data
        cleaned = clean_movie_data()
        if cleaned:
            app.logger.info(f"Cleaned {cleaned} movie records during startup")
        sync_movie_posters()
    
    return app
