"""
Pytest configuration and fixtures for testing
"""

import pytest
from app import create_app, db
from app.models import User, Movie, Genre, Rating, Watchlist


@pytest.fixture
def app():
    """Create app configured for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for making requests"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI runner for testing commands"""
    return app.test_cli_runner()


@pytest.fixture
def user(app):
    """Create a test user"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        db.session.expunge(user)
        return user


@pytest.fixture
def admin_user(app):
    """Create a test admin user"""
    with app.app_context():
        admin = User(username='admin', email='admin@example.com', is_admin=True)
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
        db.session.refresh(admin)
        db.session.expunge(admin)
        return admin


@pytest.fixture
def genres(app):
    """Create sample genres"""
    with app.app_context():
        genres_list = []
        for name in ['Action', 'Drama', 'Comedy', 'Sci-Fi']:
            genre = Genre(name=name)
            db.session.add(genre)
            genres_list.append(genre)
        db.session.commit()
        for genre in genres_list:
            db.session.refresh(genre)
            db.session.expunge(genre)
        return genres_list


@pytest.fixture
def movie(app, genres):
    """Create a sample movie"""
    with app.app_context():
        movie = Movie(
            title='Test Movie',
            description='A great test movie',
            year=2023,
            poster_url='https://example.com/poster.jpg'
        )
        first_genre = db.session.get(Genre, genres[0].id)
        movie.genres.append(first_genre)
        db.session.add(movie)
        db.session.commit()
        db.session.refresh(movie)
        db.session.expunge(movie)
        return movie


@pytest.fixture
def rating(app, user, movie):
    """Create a sample rating"""
    with app.app_context():
        persisted_user = db.session.get(User, user.id)
        persisted_movie = db.session.get(Movie, movie.id)
        rating = Rating(
            user=persisted_user,
            movie=persisted_movie,
            rating=4,
            review='Great movie!'
        )
        db.session.add(rating)
        db.session.commit()
        db.session.refresh(rating)
        db.session.expunge(rating)
        return rating
