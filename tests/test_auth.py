"""
Tests for authentication routes
"""

import pytest
from app.models import User, db


class TestAuthRoutes:
    """Tests for auth blueprint routes"""
    
    def test_register_page_loads(self, client):
        """Test register page GET request"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_register_new_user(self, client, app):
        """Test user registration"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'new@example.com'
    
    def test_register_existing_username(self, client, user):
        """Test registering with existing username"""
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }, follow_redirects=True)
        
        assert b'Username already taken' in response.data or \
               b'already' in response.data.lower()
    
    def test_register_mismatched_passwords(self, client):
        """Test registration with mismatched passwords"""
        response = client.post('/auth/register', data={
            'username': 'newuser2',
            'email': 'new2@example.com',
            'password': 'testpass123',
            'confirm_password': 'differentpass'
        }, follow_redirects=True)
        
        assert b'must match' in response.data.lower() or \
               b'password' in response.data.lower()
    
    def test_register_invalid_email(self, client):
        """Test registration with invalid email"""
        response = client.post('/auth/register', data={
            'username': 'newuser3',
            'email': 'invalidemail',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        
        assert response.status_code == 200 or response.status_code == 400
    
    def test_login_page_loads(self, client):
        """Test login page GET request"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_valid_credentials(self, client, user):
        """Test login with valid credentials"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome back' in response.data or b'dashboard' in response.data
    
    def test_login_invalid_username(self, client):
        """Test login with non-existent username"""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        assert b'Invalid' in response.data or b'username' in response.data
    
    def test_login_invalid_password(self, client, user):
        """Test login with wrong password"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert b'Invalid' in response.data or b'password' in response.data
    
    def test_logout(self, client, user):
        """Test logout"""
        # First login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Then logout
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data.lower()
    
    def test_authenticated_user_cannot_register(self, client, user):
        """Test authenticated user is redirected from register page"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.get('/auth/register', follow_redirects=False)
        assert response.status_code == 302  # Redirect
    
    def test_authenticated_user_cannot_login(self, client, user):
        """Test authenticated user is redirected from login page"""
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        response = client.get('/auth/login', follow_redirects=False)
        assert response.status_code == 302  # Redirect
