"""
Tests for movie routes
"""

import pytest
from app.models import Movie, Rating, Watchlist, db


class TestMovieRoutes:
    """Tests for movie blueprint routes"""
    
    def test_home_page_loads(self, client):
        """Test home page"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Home' in response.data or b'home' in response.data
    
    def test_movies_list_page(self, client, movie):
        """Test movies list page"""
        response = client.get('/movies')
        assert response.status_code == 200
        assert b'Test Movie' in response.data
    
    def test_movie_detail_page(self, client, movie):
        """Test movie detail page"""
        response = client.get(f'/movie/{movie.id}')
        assert response.status_code == 200
        assert b'Test Movie' in response.data
    
    def test_movie_detail_not_found(self, client):
        """Test movie detail with non-existent ID"""
        response = client.get('/movie/9999')
        assert response.status_code == 404
    
    def test_movie_search(self, client, movie):
        """Test movie search"""
        response = client.get('/search?q=Test')
        assert response.status_code == 200
        assert b'Test Movie' in response.data
    
    def test_movie_search_too_short(self, client):
        """Test search with query too short"""
        response = client.get('/search?q=a', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect or show warning
    
    def test_add_movie_requires_login(self, client):
        """Test adding movie requires authentication"""
        response = client.get('/add-movie', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_add_movie_authenticated(self, client, user, genres):
        """Test adding movie as authenticated user"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post('/add-movie', data={
            'title': 'New Movie',
            'description': 'A new test movie',
            'year': 2023,
            'poster_url': '',
            'genres': [str(genres[0].id)]
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.application.app_context():
            movie = Movie.query.filter_by(title='New Movie').first()
            assert movie is not None
    
    def test_rate_movie_requires_login(self, client, movie):
        """Test rating movie requires authentication"""
        response = client.get(f'/rate-movie/{movie.id}', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_rate_movie_authenticated(self, client, user, movie):
        """Test rating movie as authenticated user"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post(f'/rate-movie/{movie.id}', data={
            'rating': 5,
            'review': 'Excellent movie!'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.application.app_context():
            rating = Rating.query.filter_by(user_id=user.id, movie_id=movie.id).first()
            assert rating is not None
            assert rating.rating == 5
    
    def test_update_rating(self, client, user, movie, rating):
        """Test updating an existing rating"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post(f'/rate-movie/{movie.id}', data={
            'rating': 3,
            'review': 'Changed my mind'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with client.application.app_context():
            updated_rating = Rating.query.filter_by(user_id=user.id, movie_id=movie.id).first()
            assert updated_rating.rating == 3
    
    def test_watchlist_requires_login(self, client, movie):
        """Test watchlist requires authentication"""
        response = client.get('/watchlist', follow_redirects=False)
        assert response.status_code == 302
    
    def test_add_to_watchlist(self, client, user, movie):
        """Test adding movie to watchlist"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.post(f'/add-to-watchlist/{movie.id}')
        assert response.status_code == 200
        
        with client.application.app_context():
            watchlist = Watchlist.query.filter_by(user_id=user.id, movie_id=movie.id).first()
            assert watchlist is not None
    
    def test_add_to_watchlist_duplicate(self, client, user, movie):
        """Test adding movie to watchlist twice"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Add first time
        client.post(f'/add-to-watchlist/{movie.id}')
        
        # Try to add second time
        response = client.post(f'/add-to-watchlist/{movie.id}')
        assert response.status_code == 400  # Bad request
    
    def test_remove_from_watchlist(self, client, user, movie):
        """Test removing movie from watchlist"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Add to watchlist
        client.post(f'/add-to-watchlist/{movie.id}')
        
        # Remove from watchlist
        response = client.post(f'/remove-from-watchlist/{movie.id}')
        assert response.status_code == 200
        
        with client.application.app_context():
            watchlist = Watchlist.query.filter_by(user_id=user.id, movie_id=movie.id).first()
            assert watchlist is None


class TestRecommendationRoutes:
    """Tests for recommendation routes"""
    
    def test_recommendations_requires_login(self, client):
        """Test recommendations page requires authentication"""
        response = client.get('/recommendations', follow_redirects=False)
        assert response.status_code == 302
    
    def test_recommendations_no_ratings(self, client, user):
        """Test recommendations with no prior ratings"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.get('/recommendations', follow_redirects=True)
        assert response.status_code == 200
        assert b'Rate some movies' in response.data or b'rate' in response.data
    
    def test_recommendations_with_ratings(self, client, user, movie, genres):
        """Test recommendations with ratings"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Create a rating
        client.post(f'/rate-movie/{movie.id}', data={
            'rating': 5,
            'review': 'Great!'
        })
        
        response = client.get('/recommendations', follow_redirects=True)
        assert response.status_code == 200
