"""
Database models for Movie Recommendation Website
Using Flask-SQLAlchemy with SQLite
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for authentication and user information
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ratings = db.relationship('Rating', backref='user', lazy=True, cascade='all, delete-orphan')
    watchlist = db.relationship('Watchlist', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the password against the hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Movie(db.Model):
    """
    Movie model for storing movie information
    """
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    genre = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    poster_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    ratings = db.relationship('Rating', backref='movie', lazy=True, cascade='all, delete-orphan')
    watchlist = db.relationship('Watchlist', backref='movie', lazy=True, cascade='all, delete-orphan')
    
    def get_average_rating(self):
        """Calculate average rating for the movie"""
        if not self.ratings:
            return 0
        total = sum(r.rating for r in self.ratings)
        return round(total / len(self.ratings), 2)
    
    def get_rating_count(self):
        """Get total number of ratings"""
        return len(self.ratings)
    
    def __repr__(self):
        return f'<Movie {self.title}>'


class Rating(db.Model):
    """
    Rating model for user ratings and reviews
    """
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one user can only rate a movie once
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating'),)
    
    def __repr__(self):
        return f'<Rating user={self.user_id} movie={self.movie_id} rating={self.rating}>'


class Watchlist(db.Model):
    """
    Watchlist model for movies users want to watch
    """
    __tablename__ = 'watchlist'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, index=True)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint: a movie can only be in a user's watchlist once
    __table_args__ = (db.UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_watchlist'),)
    
    def __repr__(self):
        return f'<Watchlist user={self.user_id} movie={self.movie_id}>'
