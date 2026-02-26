"""
User account and dashboard routes
Handles profile, dashboard, and account management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Rating, Watchlist, User
from app.i18n import translate
from sqlalchemy import func


user_bp = Blueprint('user', __name__, url_prefix='/user')


def t(key, **kwargs):
    text = translate(key)
    return text.format(**kwargs) if kwargs else text


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing activity and statistics"""
    # Get user's recent ratings
    recent_ratings = Rating.query.filter_by(user_id=current_user.id).order_by(
        Rating.created_at.desc()
    ).limit(5).all()
    
    # Get watchlist count
    watchlist_count = Watchlist.query.filter_by(user_id=current_user.id).count()
    
    # Get rating statistics
    all_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    rating_count = len(all_ratings)
    avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings) if all_ratings else 0
    
    # Get highly rated movies (for featured section)
    highly_rated = [r.movie for r in all_ratings if r.rating >= 4]
    
    # Get rating distribution
    rating_distribution = {
        5: sum(1 for r in all_ratings if r.rating == 5),
        4: sum(1 for r in all_ratings if r.rating == 4),
        3: sum(1 for r in all_ratings if r.rating == 3),
        2: sum(1 for r in all_ratings if r.rating == 2),
        1: sum(1 for r in all_ratings if r.rating == 1),
    }
    
    return render_template('user/dashboard.html',
                         recent_ratings=recent_ratings,
                         watchlist_count=watchlist_count,
                         rating_count=rating_count,
                         avg_rating=avg_rating,
                         highly_rated=highly_rated[:6],
                         rating_distribution=rating_distribution)


@user_bp.route('/profile')
@login_required
def profile():
    """User profile page with ratings and statistics"""
    page = request.args.get('page', 1, type=int)
    
    # Get user's ratings with pagination
    user_ratings = Rating.query.filter_by(user_id=current_user.id).order_by(
        Rating.created_at.desc()
    ).paginate(page=page, per_page=10)
    
    # Calculate statistics
    all_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    rating_count = len(all_ratings)
    avg_rating = sum(r.rating for r in all_ratings) / len(all_ratings) if all_ratings else 0
    
    # Get most rated genre
    genre_stats = db.session.query(
        func.count(Rating.id).label('count')
    ).filter_by(user_id=current_user.id).join(Rating.movie).outerjoin(
        Rating.movie.genres
    ).group_by('genres.id').order_by('count'.desc()).first()
    
    return render_template('user/profile.html',
                         user=current_user,
                         user_ratings=user_ratings,
                         rating_count=rating_count,
                         avg_rating=avg_rating)


@user_bp.route('/settings')
@login_required
def settings():
    """User account settings page"""
    return render_template('user/settings.html')


@user_bp.route('/update-email', methods=['POST'])
@login_required
def update_email():
    """Update user email"""
    new_email = request.form.get('email')
    
    # Validation
    if not new_email or '@' not in new_email:
        flash(t('flash.email_invalid'), 'danger')
        return redirect(url_for('user.settings'))
    
    # Check if email already in use
    if User.query.filter_by(email=new_email).filter(User.id != current_user.id).first():
        flash(t('flash.email_in_use'), 'danger')
        return redirect(url_for('user.settings'))
    
    try:
        current_user.email = new_email
        db.session.commit()
        flash(t('flash.email_updated'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(t('flash.email_update_error'), 'danger')
    
    return redirect(url_for('user.settings'))


@user_bp.route('/update-password', methods=['POST'])
@login_required
def update_password():
    """Update user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    # Validation
    if not current_user.check_password(current_password):
        flash(t('flash.password_current_invalid'), 'danger')
        return redirect(url_for('user.settings'))
    
    if new_password != confirm_password:
        flash(t('flash.password_mismatch'), 'danger')
        return redirect(url_for('user.settings'))
    
    if len(new_password) < 6:
        flash(t('flash.password_min_length'), 'danger')
        return redirect(url_for('user.settings'))
    
    try:
        current_user.set_password(new_password)
        db.session.commit()
        flash(t('flash.password_updated'), 'success')
    except Exception as e:
        db.session.rollback()
        flash(t('flash.password_update_error'), 'danger')
    
    return redirect(url_for('user.settings'))


@user_bp.route('/my-ratings')
@login_required
def my_ratings():
    """View all user's ratings"""
    page = request.args.get('page', 1, type=int)
    sort_by = request.args.get('sort', 'recent')  # recent, rating, title
    
    query = Rating.query.filter_by(user_id=current_user.id)
    
    # Sort
    if sort_by == 'rating':
        query = query.order_by(Rating.rating.desc())
    elif sort_by == 'title':
        query = query.join(Rating.movie).order_by(db.func.lower(db.func.substr('movies.title', 1, 1)).asc())
    else:  # recent (default)
        query = query.order_by(Rating.created_at.desc())
    
    ratings = query.paginate(page=page, per_page=15)
    
    return render_template('user/my_ratings.html',
                         ratings=ratings,
                         sort_by=sort_by)


@user_bp.route('/stats')
@login_required
def stats():
    """Detailed user statistics and activity"""
    # Get all ratings for analysis
    all_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    
    # Rating statistics
    rating_stats = {
        'total': len(all_ratings),
        'average': sum(r.rating for r in all_ratings) / len(all_ratings) if all_ratings else 0,
        'distribution': {
            5: sum(1 for r in all_ratings if r.rating == 5),
            4: sum(1 for r in all_ratings if r.rating == 4),
            3: sum(1 for r in all_ratings if r.rating == 3),
            2: sum(1 for r in all_ratings if r.rating == 2),
            1: sum(1 for r in all_ratings if r.rating == 1),
        }
    }
    
    # Watchlist statistics
    watchlist_count = Watchlist.query.filter_by(user_id=current_user.id).count()
    
    # Genre preferences (top 5)
    genre_preferences = db.session.query(
        'genres.name',
        func.count(Rating.id).label('count')
    ).filter_by(user_id=current_user.id).join(
        Rating.movie
    ).join(
        'movies.genres'
    ).group_by('genres.id').order_by(
        'count'.desc()
    ).limit(5).all()
    
    return render_template('user/stats.html',
                         rating_stats=rating_stats,
                         watchlist_count=watchlist_count,
                         genre_preferences=genre_preferences)
