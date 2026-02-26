"""
Admin panel and management routes
Restricted to admin users only
"""

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models import db, User, Movie, Rating, Watchlist, Genre
from app.i18n import translate
from app.services.posters import sync_movie_details_with_tmdb, remove_movies_with_placeholder_posters
from sqlalchemy import func


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def t(key, **kwargs):
    text = translate(key)
    return text.format(**kwargs) if kwargs else text


def admin_required(f):
    """Decorator to restrict route to admin users only"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash(t('admin.no_permission'), 'danger')
            return redirect(url_for('movie.home'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard with statistics and management options"""
    # Get statistics
    total_users = User.query.count()
    total_movies = Movie.query.count()
    total_ratings = Rating.query.count()
    total_watchlist = Watchlist.query.count()
    
    # Get recent activities
    recent_ratings = Rating.query.order_by(Rating.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Get top-rated movies
    top_movies = db.session.query(
        Movie,
        func.avg(Rating.rating).label('avg_rating'),
        func.count(Rating.id).label('rating_count')
    ).outerjoin(Rating).group_by(Movie.id).order_by(
        func.avg(Rating.rating).desc()
    ).limit(5).all()
    
    # Get most active users
    active_users = db.session.query(
        User,
        func.count(Rating.id).label('rating_count')
    ).outerjoin(Rating).group_by(User.id).order_by(
        'rating_count'.desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_movies=total_movies,
                         total_ratings=total_ratings,
                         total_watchlist=total_watchlist,
                         recent_ratings=recent_ratings,
                         recent_users=recent_users,
                         top_movies=top_movies,
                         active_users=active_users)


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    """Manage users - view and modify"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = User.query
    
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/manage_users.html',
                         users=users,
                         search=search)


@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    """View detailed user information"""
    user = db.get_or_404(User, user_id)
    
    # Get user statistics
    ratings = Rating.query.filter_by(user_id=user_id).all()
    watchlist = Watchlist.query.filter_by(user_id=user_id).all()
    
    stats = {
        'ratings_count': len(ratings),
        'avg_rating': sum(r.rating for r in ratings) / len(ratings) if ratings else 0,
        'watchlist_count': len(watchlist)
    }
    
    return render_template('admin/view_user.html',
                         user=user,
                         ratings=ratings,
                         watchlist=watchlist,
                         stats=stats)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for a user"""
    user = db.get_or_404(User, user_id)
    
    # Prevent removing own admin status
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': t('admin.cannot_modify_self')}), 400
    
    try:
        user.is_admin = not user.is_admin
        db.session.commit()
        
        status = 'Admin' if user.is_admin else 'User'
        flash(f'{user.username} is now a {status}.', 'success')
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': t('admin.user_updated_error')}), 500


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user account"""
    user = db.get_or_404(User, user_id)
    
    # Prevent deleting own account
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': t('admin.cannot_delete_self')}), 400
    
    try:
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        flash(t('admin.user_deleted', username=username), 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': t('admin.user_delete_error')}), 500


@admin_bp.route('/movies')
@login_required
@admin_required
def manage_movies():
    """Manage movies in the database"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = Movie.query
    
    if search:
        query = query.filter(
            (Movie.title.ilike(f'%{search}%')) |
            (Movie.description.ilike(f'%{search}%'))
        )
    
    movies = query.order_by(Movie.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/manage_movies.html',
                         movies=movies,
                         search=search)


@admin_bp.route('/movies/<int:movie_id>')
@login_required
@admin_required
def view_movie(movie_id):
    """View detailed movie information with admin options"""
    movie = db.get_or_404(Movie, movie_id)
    
    # Get movie statistics
    ratings = Rating.query.filter_by(movie_id=movie_id).all()
    watchlist = Watchlist.query.filter_by(movie_id=movie_id).all()
    
    stats = {
        'ratings_count': len(ratings),
        'avg_rating': movie.get_average_rating_db(),
        'watchlist_count': len(watchlist)
    }
    
    return render_template('admin/view_movie.html',
                         movie=movie,
                         ratings=ratings,
                         stats=stats)


@admin_bp.route('/movies/<int:movie_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_movie(movie_id):
    """Delete a movie"""
    movie = db.get_or_404(Movie, movie_id)
    
    try:
        title = movie.title
        db.session.delete(movie)
        db.session.commit()
        
        flash(t('admin.movie_deleted', title=title), 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': t('admin.movie_delete_error')}), 500


@admin_bp.route('/ratings')
@login_required
@admin_required
def manage_ratings():
    """Manage all ratings in the system"""
    page = request.args.get('page', 1, type=int)
    
    ratings = Rating.query.order_by(Rating.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/manage_ratings.html', ratings=ratings)


@admin_bp.route('/ratings/<int:rating_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_rating(rating_id):
    """Delete a rating"""
    rating = db.get_or_404(Rating, rating_id)
    
    try:
        movie_id = rating.movie_id
        db.session.delete(rating)
        db.session.commit()
        
        flash(t('admin.rating_deleted'), 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': t('admin.rating_delete_error')}), 500


@admin_bp.route('/genres')
@login_required
@admin_required
def manage_genres():
    """Manage movie genres"""
    page = request.args.get('page', 1, type=int)
    
    genres = Genre.query.order_by(Genre.name).paginate(page=page, per_page=20)
    
    return render_template('admin/manage_genres.html', genres=genres)


@admin_bp.route('/genres/add', methods=['POST'])
@login_required
@admin_required
def add_genre():
    """Add a new genre"""
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    
    if not name:
        flash(t('admin.genre_name_required'), 'danger')
        return redirect(url_for('admin.manage_genres'))
    
    # Check if genre already exists
    if Genre.query.filter_by(name=name).first():
        flash(t('admin.genre_exists'), 'warning')
        return redirect(url_for('admin.manage_genres'))
    
    try:
        genre = Genre(name=name, description=description)
        db.session.add(genre)
        db.session.commit()
        flash(t('admin.genre_added', name=name), 'success')
    except Exception as e:
        db.session.rollback()
        flash(t('admin.genre_add_error'), 'danger')
    
    return redirect(url_for('admin.manage_genres'))


@admin_bp.route('/genres/<int:genre_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_genre(genre_id):
    """Delete a genre"""
    genre = db.get_or_404(Genre, genre_id)
    
    try:
        name = genre.name
        db.session.delete(genre)
        db.session.commit()
        
        flash(t('admin.genre_deleted', name=name), 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': t('admin.genre_delete_error')}), 500


@admin_bp.route('/stats')
@login_required
@admin_required
def stats():
    """Detailed admin statistics and analytics"""
    # User statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(is_admin=True).count()
    
    # Movie and Rating statistics
    total_movies = Movie.query.count()
    total_ratings = Rating.query.count()
    avg_rating = db.session.query(func.avg(Rating.rating)).scalar() or 0
    
    # Watchlist statistics
    total_watchlist = Watchlist.query.count()
    
    # Growth data (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    new_users = User.query.filter(User.created_at >= thirty_days_ago).count()
    new_ratings = Rating.query.filter(Rating.created_at >= thirty_days_ago).count()
    new_movies = Movie.query.filter(Movie.created_at >= thirty_days_ago).count()
    
    return render_template('admin/stats.html',
                         total_users=total_users,
                         admin_users=admin_users,
                         total_movies=total_movies,
                         total_ratings=total_ratings,
                         avg_rating=avg_rating,
                         total_watchlist=total_watchlist,
                         new_users=new_users,
                         new_ratings=new_ratings,
                         new_movies=new_movies)


@admin_bp.route('/sync-movie-details', methods=['GET', 'POST'])
@login_required
@admin_required
def sync_movie_details():
    """Synchronize movie titles, descriptions, and details with TMDB poster data"""
    if request.method == 'POST':
        try:
            result = sync_movie_details_with_tmdb()
            
            flash(
                t('admin.sync_complete', 
                  total=result['total'],
                  updated=result['updated'],
                  unchanged=result['unchanged'],
                  failed=result['failed']),
                'success'
            )
            
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            flash(t('admin.sync_error', error=str(e)), 'danger')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return render_template('admin/sync_movie_details.html')


@admin_bp.route('/remove-placeholder-movies', methods=['GET', 'POST'])
@login_required
@admin_required
def remove_placeholder_movies():
    """Remove movies that have only placeholder posters (not real TMDB posters)"""
    if request.method == 'POST':
        try:
            result = remove_movies_with_placeholder_posters()
            
            flash(
                t('admin.placeholder_removed',
                  removed=result['removed'],
                  ratings=result['ratings_removed'],
                  watchlist=result['watchlist_removed']),
                'success'
            )
            
            return jsonify({
                'success': True,
                'result': result
            })
        except Exception as e:
            flash(t('admin.placeholder_error', error=str(e)), 'danger')
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    return render_template('admin/remove_placeholder_movies.html')
