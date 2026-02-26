"""
Script to synchronize movie titles, descriptions, and details with TMDB poster data.

This ensures that movie information (name, plot, details) matches the TMDB data
associated with their posters.
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env so TMDB_API_KEY is available
load_dotenv()
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
from app.services.posters import sync_movie_details_with_tmdb

app = create_app()
with app.app_context():
    print('Synchronizing movie details with TMDB data...')
    print('This may take a few moments...\n')
    
    result = sync_movie_details_with_tmdb()
    
    print(f'\n✓ Synchronization Complete!')
    print(f'  Total movies processed: {result["total"]}')
    print(f'  ✓ Updated: {result["updated"]}')
    print(f'  → Unchanged: {result["unchanged"]}')
    print(f'  ✗ Failed: {result["failed"]}')
