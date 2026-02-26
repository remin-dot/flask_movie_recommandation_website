"""
TMDB (The Movie Database) API integration service
Fetches movie data including posters, descriptions, genres, and ratings
"""

import requests
from flask import current_app
from app.models import db, Movie, Genre


class TMDBService:
    """Service for integrating with TMDB API"""
    
    def __init__(self):
        """Initialize TMDB service with API key from config"""
        self.api_key = current_app.config.get('TMDB_API_KEY', '')
        self.base_url = current_app.config.get('TMDB_BASE_URL', 'https://api.themoviedb.org/3')
        self.image_base_url = current_app.config.get('TMDB_IMAGE_BASE_URL', 'https://image.tmdb.org/t/p/w500')
    
    def search_movies(self, query, page=1):
        """
        Search for movies on TMDB
        
        Args:
            query: Search query (movie title)
            page: Page number for pagination
        
        Returns:
            List of movie data dictionaries or empty list if API error
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': query,
                'page': page,
                'language': 'en-US'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
        
        except Exception as e:
            print(f"TMDB search error: {str(e)}")
            return []
    
    def get_movie_details(self, tmdb_id):
        """
        Get detailed information about a movie
        
        Args:
            tmdb_id: TMDB movie ID
        
        Returns:
            Dictionary with movie details or None if error
        """
        if not self.api_key:
            return None
        
        try:
            url = f"{self.base_url}/movie/{tmdb_id}"
            params = {
                'api_key': self.api_key,
                'language': 'en-US'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            return response.json()
        
        except Exception as e:
            print(f"TMDB details error: {str(e)}")
            return None
    
    def import_movie_from_tmdb(self, tmdb_id):
        """
        Import a movie from TMDB and add it to the database
        
        Args:
            tmdb_id: TMDB movie ID
        
        Returns:
            Tuple (success: bool, movie_or_message: Movie or str)
        """
        # Check if movie already imported
        existing = Movie.query.filter_by(tmdb_id=tmdb_id).first()
        if existing:
            return True, existing
        
        # Get movie details from TMDB
        details = self.get_movie_details(tmdb_id)
        if not details:
            return False, "Could not fetch movie details from TMDB"
        
        try:
            # Extract relevant data
            title = details.get('title')
            description = details.get('overview')
            year = None
            
            release_date = details.get('release_date')
            if release_date:
                year = int(release_date.split('-')[0])
            
            poster_path = details.get('poster_path')
            poster_url = f"{self.image_base_url}{poster_path}" if poster_path else None
            
            # Create movie object
            movie = Movie(
                title=title,
                description=description or 'No description available',
                year=year,
                poster_url=poster_url,
                tmdb_id=tmdb_id
            )
            
            # Add genres from TMDB
            if details.get('genres'):
                for genre_data in details['genres']:
                    genre_name = genre_data.get('name')
                    
                    # Find or create genre
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if not genre:
                        genre = Genre(name=genre_name)
                        db.session.add(genre)
                    
                    movie.genres.append(genre)
            
            db.session.add(movie)
            db.session.commit()
            
            return True, movie
        
        except Exception as e:
            db.session.rollback()
            return False, f"Error importing movie: {str(e)}"
    
    def search_and_import(self, query):
        """
        Search for movies and present options for import
        
        Args:
            query: Search query
        
        Returns:
            List of search results with TMD B data
        """
        results = self.search_movies(query)
        
        formatted_results = []
        for result in results[:10]:  # Limit to top 10 results
            tmdb_id = result.get('id')
            
            # Skip if already in database
            if Movie.query.filter_by(tmdb_id=tmdb_id).first():
                continue
            
            formatted_results.append({
                'tmdb_id': tmdb_id,
                'title': result.get('title'),
                'year': result.get('release_date', '').split('-')[0] if result.get('release_date') else None,
                'overview': result.get('overview'),
                'poster_path': result.get('poster_path'),
                'rating': result.get('vote_average')
            })
        
        return formatted_results
    
    def get_popular_movies(self, page=1):
        """
        Get popular movies from TMDB
        
        Args:
            page: Page number
        
        Returns:
            List of popular movie data
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/movie/popular"
            params = {
                'api_key': self.api_key,
                'language': 'en-US',
                'page': page
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])
        
        except Exception as e:
            print(f"TMDB popular movies error: {str(e)}")
            return []
    
    def get_movie_recommendations(self, tmdb_id):
        """
        Get recommendations from TMDB for a given movie
        
        Args:
            tmdb_id: TMDB movie ID
        
        Returns:
            List of recommendation data
        """
        if not self.api_key:
            return []
        
        try:
            url = f"{self.base_url}/movie/{tmdb_id}/recommendations"
            params = {
                'api_key': self.api_key,
                'language': 'en-US'
            }
            
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            return data.get('results', [])[:10]  # Return top 10
        
        except Exception as e:
            print(f"TMDB recommendations error: {str(e)}")
            return []


def create_tmdb_service():
    """Factory function to create TMDB service instance"""
    return TMDBService()
