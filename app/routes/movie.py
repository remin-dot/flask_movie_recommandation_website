"""
Movie management and display routes
Handles listing, searching, rating, and watchlist operations
"""

import logging
from flask import (Blueprint, render_template, request, redirect, url_for, 
                   flash, jsonify)
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from sqlalchemy import func, case
from sqlalchemy.orm import joinedload
from app.models import db, Movie, Rating, Watchlist, Genre
from app.i18n import get_current_language, translate
from app.services.recommendations import RecommendationService
from app.services.posters import get_poster_for_movie
from app.services.search_index import search_index
from app.utils import validate_search_query, validate_rating

logger = logging.getLogger(__name__)


def t(key, **kwargs):
    text = translate(key)
    return text.format(**kwargs) if kwargs else text


movie_bp = Blueprint('movie', __name__)


class SimplePagination:
    """Lightweight pagination helper for list-based results."""

    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total

    @property
    def pages(self):
        if self.total == 0:
            return 0
        return (self.total + self.per_page - 1) // self.per_page

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    @property
    def prev_num(self):
        return self.page - 1

    @property
    def next_num(self):
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=2, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (self.page - left_current - 1 < num < self.page + right_current)
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


class MovieForm(FlaskForm):
    """Form for adding/editing movies"""
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=1, max=255)
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10)
    ])
    year = IntegerField('Year', validators=[
        DataRequired(),
        NumberRange(min=1800, max=2100)
    ])
    poster_url = StringField('Poster URL (optional)', validators=[Length(max=500)])
    genres = SelectMultipleField('Genres', coerce=int)
    submit = SubmitField('Save Movie')


class RatingForm(FlaskForm):
    """Form for rating movies"""
    rating = IntegerField('Rating (1-5)', validators=[
        DataRequired(),
        NumberRange(min=1, max=5)
    ])
    review = TextAreaField('Review (optional)', validators=[Length(max=1000)])
    submit = SubmitField('Submit Rating')


@movie_bp.route('/')
def home():
    """Home page with featured and trending movies"""
    # Get featured movies (recently added)
    featured = Movie.query.order_by(Movie.created_at.desc()).limit(6).all()
    
    # Get trending movies (highest rated recently)
    trending = db.session.query(Movie).join(Rating).group_by(Movie.id).order_by(
        func.avg(Rating.rating).desc()
    ).limit(6).all()
    
    return render_template('home.html', 
                         featured_movies=featured,
                         trending_movies=trending)


@movie_bp.route('/movies')
def movies():
    """Movie list with filtering and pagination"""
    page = request.args.get('page', 1, type=int)
    genre_id = request.args.get('genre', type=int)
    sort_by = request.args.get('sort', 'recent')  # recent, rating, oldest
    
    query = Movie.query
    
    # Filter by genre if provided
    if genre_id:
        query = query.join(Movie.genres).filter(Genre.id == genre_id)
    
    # Sort
    if sort_by == 'rating':
        # Join with ratings and sort by average rating
        query = query.outerjoin(Rating).group_by(Movie.id).order_by(
            func.avg(Rating.rating).desc()
        )
    elif sort_by == 'oldest':
        query = query.order_by(Movie.year.asc())
    else:  # recent (default)
        query = query.order_by(Movie.created_at.desc())
    
    movies = query.paginate(page=page, per_page=12)
    genres = Genre.query.order_by(Genre.name).all()
    
    return render_template('movies/list.html', 
                         movies=movies,
                         genres=genres,
                         selected_genre=genre_id,
                         sort_by=sort_by)


@movie_bp.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    """Display detailed movie information with ratings"""
    movie = db.get_or_404(Movie, movie_id)
    
    # Get ratings for this movie
    ratings = Rating.query.filter_by(movie_id=movie_id).order_by(
        Rating.created_at.desc()
    ).all()
    
    # Get user's rating if authenticated
    user_rating = None
    in_watchlist = False
    
    if current_user.is_authenticated:
        user_rating = Rating.query.filter_by(
            user_id=current_user.id,
            movie_id=movie_id
        ).first()
        in_watchlist = Watchlist.query.filter_by(
            user_id=current_user.id,
            movie_id=movie_id
        ).first() is not None
    
    # Calculate average rating and count
    avg_rating = movie.get_average_rating_db()
    rating_count = len(ratings)
    
    return render_template('movies/detail.html',
                         movie=movie,
                         ratings=ratings,
                         user_rating=user_rating,
                         in_watchlist=in_watchlist,
                         avg_rating=avg_rating,
                         rating_count=rating_count)


@movie_bp.route('/add-movie', methods=['GET', 'POST'])
@login_required
def add_movie():
    """Add a new movie to the database"""
    # Only admins or authenticated users can add movies
    form = MovieForm()
    form.genres.choices = [(g.id, g.name) for g in Genre.query.order_by(Genre.name).all()]
    
    if form.validate_on_submit():
        try:
            # Check if movie already exists
            existing = Movie.query.filter_by(
                title=form.title.data,
                year=form.year.data
            ).first()
            
            if existing:
                flash(t('flash.movie_exists'), 'warning')
                return redirect(url_for('movie.movie_detail', movie_id=existing.id))
            
            # Create new movie
            movie = Movie(
                title=form.title.data,
                description=form.description.data,
                year=form.year.data,
                poster_url=form.poster_url.data or get_poster_for_movie(form.title.data, form.year.data)
            )
            
            # Add genres
            selected_genres = Genre.query.filter(Genre.id.in_(form.genres.data)).all()
            movie.genres.extend(selected_genres)
            
            db.session.add(movie)
            db.session.commit()
            search_index.invalidate()
            
            flash(t('flash.movie_added', title=movie.title), 'success')
            return redirect(url_for('movie.movie_detail', movie_id=movie.id))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error adding movie: {str(e)}")
            flash(t('flash.movie_add_error'), 'danger')
    
    return render_template('movies/add.html', form=form)


@movie_bp.route('/rate-movie/<int:movie_id>', methods=['GET', 'POST'])
@login_required
def rate_movie(movie_id):
    """Rate and review a movie"""
    movie = db.get_or_404(Movie, movie_id)
    existing_rating = Rating.query.filter_by(
        user_id=current_user.id,
        movie_id=movie_id
    ).first()
    
    form = RatingForm()
    
    if form.validate_on_submit():
        try:
            if existing_rating:
                # Update existing rating
                existing_rating.rating = form.rating.data
                existing_rating.review = form.review.data
                message = t('flash.rating_updated')
            else:
                # Create new rating
                rating = Rating(
                    user_id=current_user.id,
                    movie_id=movie_id,
                    rating=form.rating.data,
                    review=form.review.data
                )
                db.session.add(rating)
                message = t('flash.rating_saved')
            
            db.session.commit()
            flash(message, 'success')
            return redirect(url_for('movie.movie_detail', movie_id=movie_id))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving rating for movie {movie_id}: {str(e)}")
            flash(t('flash.rating_save_error'), 'danger')
    
    elif existing_rating:
        form.rating.data = existing_rating.rating
        form.review.data = existing_rating.review
    
    return render_template('movies/rate.html', movie=movie, form=form)


@movie_bp.route('/delete-rating/<int:rating_id>', methods=['POST'])
@login_required
def delete_rating(rating_id):
    """Delete a user's rating"""
    rating = db.get_or_404(Rating, rating_id)
    
    # Verify ownership
    if rating.user_id != current_user.id:
        return jsonify({'success': False, 'message': t('api.unauthorized')}), 403
    
    try:
        movie_id = rating.movie_id
        db.session.delete(rating)
        db.session.commit()
        logger.info(f"Rating {rating_id} deleted by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': t('api.rating_deleted')
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting rating {rating_id}: {str(e)}")
        return jsonify({
            'success': False,
            'message': t('api.rating_delete_error')
        }), 500


@movie_bp.route('/watchlist')
@login_required
def watchlist():
    """Display user's watchlist"""
    page = request.args.get('page', 1, type=int)
    # Optimize query with eager loading of related movie data
    watchlist_items = db.session.query(Watchlist).options(
        joinedload(Watchlist.movie)
    ).filter_by(
        user_id=current_user.id
    ).order_by(Watchlist.added_at.desc()).paginate(page=page, per_page=12)
    
    return render_template('movies/watchlist.html', watchlist=watchlist_items)


@movie_bp.route('/add-to-watchlist/<int:movie_id>', methods=['POST'])
@login_required
def add_to_watchlist(movie_id):
    """Add movie to watchlist (AJAX)"""
    movie = db.get_or_404(Movie, movie_id)
    
    # Check if already in watchlist
    if Watchlist.query.filter_by(user_id=current_user.id, movie_id=movie_id).first():
        return jsonify({
            'success': False,
            'message': t('api.watchlist_exists')
        }), 400
    
    try:
        watchlist = Watchlist(user_id=current_user.id, movie_id=movie_id)
        db.session.add(watchlist)
        db.session.commit()
        logger.info(f"Movie {movie_id} added to watchlist by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': t('api.watchlist_added', title=movie.title)
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding movie {movie_id} to watchlist: {str(e)}")
        return jsonify({
            'success': False,
            'message': t('api.watchlist_add_error')
        }), 500


@movie_bp.route('/remove-from-watchlist/<int:movie_id>', methods=['POST'])
@login_required
def remove_from_watchlist(movie_id):
    """Remove movie from watchlist (AJAX)"""
    watchlist = Watchlist.query.filter_by(
        user_id=current_user.id,
        movie_id=movie_id
    ).first_or_404()
    
    try:
        movie = db.session.get(Movie, movie_id)
        db.session.delete(watchlist)
        db.session.commit()
        logger.info(f"Movie {movie_id} removed from watchlist by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': t('api.watchlist_removed', title=movie.title)
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing movie {movie_id} from watchlist: {str(e)}")
        return jsonify({
            'success': False,
            'message': t('api.watchlist_remove_error')
        }), 500


@movie_bp.route('/search')
def search():
    """Search movies by title, description, or genre"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    if not query or len(query) < 2:
        flash(t('flash.search_min'), 'warning')
        return redirect(url_for('movie.home'))
    
    try:
        # Validate and sanitize search query
        sanitized_query = validate_search_query(query)
        
        current_lang = get_current_language()
        matched_ids = search_index.search_ids(sanitized_query, current_lang)
        total = len(matched_ids)
        start = (page - 1) * per_page
        end = start + per_page
        page_ids = matched_ids[start:end]

        if page_ids:
            ordering = case({movie_id: index for index, movie_id in enumerate(page_ids)}, value=Movie.id)
            items = (
                Movie.query
                .options(joinedload(Movie.genres))
                .filter(Movie.id.in_(page_ids))
                .order_by(ordering)
                .all()
            )
        else:
            items = []

        results = SimplePagination(items, page, per_page, total)
        
        return render_template('movies/search.html',
                             results=results,
                             search_query=sanitized_query)
    
    except Exception as e:
        logger.error(f"Search error for query '{query}': {str(e)}")
        flash(t('flash.search_error'), 'danger')
        return redirect(url_for('movie.home'))


@movie_bp.route('/search/suggest')
def search_suggest():
    """Return search suggestions based on current language."""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'suggestions': []})

    try:
        # Validate and sanitize search query
        sanitized_query = validate_search_query(query)
        current_lang = get_current_language()
        suggestions = search_index.suggest(sanitized_query, current_lang, limit=8)
        return jsonify({'suggestions': suggestions})
    
    except Exception as e:
        logger.error(f"Search suggestion error for query '{query}': {str(e)}")
        return jsonify({'suggestions': [], 'error': str(e)}), 500


@movie_bp.route('/recommendations')
@login_required
def recommendations():
    """Get personalized movie recommendations"""
    algo = request.args.get('algorithm', 'combined')  # combined, genre, popularity, collaborative
    
    if algo == 'genre':
        recs = RecommendationService.get_genre_based_recommendations(current_user.id)
        algo_name = t('recs.algo_genre')
    elif algo == 'popularity':
        recs = RecommendationService.get_popularity_based_recommendations(current_user.id)
        algo_name = t('recs.algo_popular')
    elif algo == 'collaborative':
        recs = RecommendationService.get_collaborative_filtering_recommendations(current_user.id)
        algo_name = t('recs.algo_collab')
    else:
        recs = RecommendationService.get_combined_recommendations(current_user.id)
        algo_name = t('recs.algo_combined')
    
    if not recs:
        flash(t('flash.recs_prompt'), 'info')
    
    return render_template('movies/recommendations.html',
                         recommendations=recs,
                         algorithm=algo,
                         algo_name=algo_name)
