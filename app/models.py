"""
Database models for Movie Recommendation Website
Enhanced with poster URLs, normalized genres, and improved relationships
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, UTC
from sqlalchemy import func

db = SQLAlchemy()


def utcnow():
    return datetime.now(UTC)

# Association table for Movie-Genre many-to-many relationship
movie_genre = db.Table(
    'movie_genre',
    db.Column('movie_id', db.Integer, db.ForeignKey('movies.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)


class User(UserMixin, db.Model):
    """
    User model for authentication and user information
    
    Attributes:
        id: Primary key
        username: Unique username
        email: Unique email address
        password_hash: Hashed password
        is_admin: Whether user has admin privileges
        created_at: Account creation timestamp
        ratings: Relationship to user's ratings
        watchlist: Relationship to user's watchlist items
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    ratings = db.relationship('Rating', backref='user', lazy=True, cascade='all, delete-orphan')
    watchlist = db.relationship('Watchlist', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against the hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_average_rating(self):
        """Get user's average rating across all movies"""
        if not self.ratings:
            return 0
        total = sum(r.rating for r in self.ratings)
        return round(total / len(self.ratings), 2)
    
    def get_rating_count(self):
        """Get total number of movies rated by user"""
        return len(self.ratings)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Genre(db.Model):
    """
    Genre model for normalized genre storage
    
    Attributes:
        id: Primary key
        name: Genre name (e.g., 'Action', 'Drama')
        description: Genre description
        movies: Relationship to movies with this genre
    """
    __tablename__ = 'genres'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    
    # Relationship
    movies = db.relationship('Movie', secondary=movie_genre, backref=db.backref('genres', lazy='select'))
    
    def __repr__(self):
        return f'<Genre {self.name}>'


class Movie(db.Model):
    """
    Movie model for storing movie information
    
    Attributes:
        id: Primary key
        title: Movie title
        description: Movie description/plot
        year: Release year
        poster_url: URL to movie poster image
        tmdb_id: External TMDB API ID for integration
        created_at: When movie was added to database
        updated_at: Last modification timestamp
        ratings: Relationship to ratings
        watchlist: Relationship to watchlist items
    """
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False, index=True)
    poster_url = db.Column(db.String(500), nullable=True)  # URL to poster image
    tmdb_id = db.Column(db.Integer, nullable=True, unique=True, index=True)  # For TMDB API integration
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
    # Relationships
    ratings = db.relationship('Rating', backref='movie', lazy=True, cascade='all, delete-orphan')
    watchlist = db.relationship('Watchlist', backref='movie', lazy=True, cascade='all, delete-orphan')
    
    def get_average_rating(self):
        """Calculate average rating for the movie"""
        if not self.ratings:
            return 0
        total = sum(r.rating for r in self.ratings)
        return round(total / len(self.ratings), 2)
    
    def get_average_rating_db(self):
        """Get average rating from database (more efficient for large datasets)"""
        avg = db.session.query(func.avg(Rating.rating)).filter_by(movie_id=self.id).scalar()
        return round(avg, 2) if avg else 0
    
    def get_rating_count(self):
        """Get total number of ratings"""
        return len(self.ratings)
    
    def get_genre_names(self):
        """Get list of genre names for this movie"""
        return [genre.name for genre in self.genres]
    
    def __repr__(self):
        return f'<Movie {self.title} ({self.year})>'


class Rating(db.Model):
    """
    Rating model for user ratings and reviews
    
    Attributes:
        id: Primary key
        user_id: Foreign key to user
        movie_id: Foreign key to movie
        rating: Rating value (1-5 stars)
        review: Text review/comment
        created_at: When rating was created
        updated_at: When rating was last updated
    """
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    
    # Unique constraint: one user can only rate a movie once
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating'),)
    
    def __repr__(self):
        return f'<Rating user_id={self.user_id} movie_id={self.movie_id} rating={self.rating}>'


class Watchlist(db.Model):
    """
    Watchlist model for movies users want to watch
    
    Attributes:
        id: Primary key
        user_id: Foreign key to user
        movie_id: Foreign key to movie
        added_at: When movie was added to watchlist
    """
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=utcnow, index=True)
    
    # Unique constraint: a movie can only be in a user's watchlist once
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_watchlist'),)
    
    def __repr__(self):
        return f'<Watchlist user_id={self.user_id} movie_id={self.movie_id}>'
