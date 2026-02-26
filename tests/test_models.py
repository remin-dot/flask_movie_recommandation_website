"""
Unit tests for database models
"""

import pytest
from app.models import User, Movie, Genre, Rating, Watchlist, db


class TestUserModel:
    """Tests for User model"""
    
    def test_user_creation(self, app, user):
        """Test creating a user"""
        with app.app_context():
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password_hash is not None
    
    def test_password_hashing(self, app):
        """Test password hashing"""
        with app.app_context():
            user = User(username='testuser2', email='test2@example.com')
            user.set_password('mypassword')
            
            assert not (user.password_hash == 'mypassword')
            assert user.check_password('mypassword')
            assert not user.check_password('wrongpassword')
    
    def test_admin_user(self, app, admin_user):
        """Test admin user creation"""
        with app.app_context():
            assert admin_user.is_admin == True
    
    def test_user_repr(self, user):
        """Test user string representation"""
        assert repr(user) == '<User testuser>'


class TestGenreModel:
    """Tests for Genre model"""
    
    def test_genre_creation(self, app, genres):
        """Test creating genres"""
        with app.app_context():
            assert len(genres) == 4
            assert genres[0].name == 'Action'
    
    def test_genre_repr(self, genres):
        """Test genre string representation"""
        assert repr(genres[0]) == '<Genre Action>'


class TestMovieModel:
    """Tests for Movie model"""
    
    def test_movie_creation(self, app, movie):
        """Test creating a movie"""
        with app.app_context():
            assert movie.title == 'Test Movie'
            assert movie.year == 2023
            assert movie.description == 'A great test movie'
    
    def test_movie_genres(self, app, movie, genres):
        """Test adding genres to movie"""
        with app.app_context():
            persisted_movie = db.session.get(Movie, movie.id)
            persisted_movie.genres.append(db.session.get(Genre, genres[1].id))
            persisted_movie.genres.append(db.session.get(Genre, genres[2].id))
            assert len(persisted_movie.genres) == 3
            assert 'Drama' in [g.name for g in persisted_movie.genres]
    
    def test_get_average_rating(self, app, movie, user):
        """Test average rating calculation"""
        with app.app_context():
            persisted_user = db.session.get(User, user.id)
            persisted_movie = db.session.get(Movie, movie.id)
            rating1 = Rating(user=persisted_user, movie=persisted_movie, rating=5)
            user2 = User(username='user2', email='user2@example.com')
            user2.set_password('pass123')
            rating2 = Rating(user=user2, movie=persisted_movie, rating=3)
            
            db.session.add(user2)
            db.session.add(rating1)
            db.session.add(rating2)
            db.session.commit()
            
            assert persisted_movie.get_average_rating() == 4.0
    
    def test_movie_repr(self, movie):
        """Test movie string representation"""
        assert repr(movie) == '<Movie Test Movie (2023)>'


class TestRatingModel:
    """Tests for Rating model"""
    
    def test_rating_creation(self, app, rating, user, movie):
        """Test creating a rating"""
        with app.app_context():
            persisted_user = db.session.get(User, user.id)
            persisted_movie = db.session.get(Movie, movie.id)
            persisted_rating = db.session.get(Rating, rating.id)
            assert persisted_rating.rating == 4
            assert persisted_rating.review == 'Great movie!'
            assert persisted_rating.user == persisted_user
            assert persisted_rating.movie == persisted_movie
    
    def test_rating_validation(self, app, user, movie):
        """Test rating validation"""
        with app.app_context():
            rating = Rating(user_id=user.id, movie_id=movie.id, rating=5, review='')
            db.session.add(rating)
            db.session.commit()
            
            assert rating.rating == 5
    
    def test_unique_user_movie_rating(self, app, user, movie):
        """Test unique constraint on user-movie-rating"""
        with app.app_context():
            rating1 = Rating(user_id=user.id, movie_id=movie.id, rating=4)
            rating2 = Rating(user_id=user.id, movie_id=movie.id, rating=5)
            
            db.session.add(rating1)
            db.session.commit()
            
            db.session.add(rating2)
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()


class TestWatchlistModel:
    """Tests for Watchlist model"""
    
    def test_watchlist_creation(self, app, user, movie):
        """Test adding movie to watchlist"""
        with app.app_context():
            watchlist = Watchlist(user_id=user.id, movie_id=movie.id)
            db.session.add(watchlist)
            db.session.commit()
            
            assert watchlist.user_id == user.id
            assert watchlist.movie_id == movie.id
    
    def test_unique_watchlist_entry(self, app, user, movie):
        """Test unique constraint on watchlist"""
        with app.app_context():
            w1 = Watchlist(user_id=user.id, movie_id=movie.id)
            w2 = Watchlist(user_id=user.id, movie_id=movie.id)
            
            db.session.add(w1)
            db.session.commit()
            
            db.session.add(w2)
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()
