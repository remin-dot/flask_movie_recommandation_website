"""
Script to remove movies that have only placeholder posters (not real TMDB posters).

Placeholder posters (from placehold.co) indicate movies without actual poster artwork.
This script removes such movies along with their ratings and watchlist entries.
"""
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
from app.services.posters import remove_movies_with_placeholder_posters

app = create_app()
with app.app_context():
    print('Removing movies with placeholder posters...')
    print('This will delete movies that do not have real TMDB poster images.\n')
    
    # Confirm before proceeding
    response = input('Are you sure? This will permanently delete movies. (yes/no): ').strip().lower()
    if response not in ['yes', 'y']:
        print('❌ Cancelled.')
        exit(0)
    
    result = remove_movies_with_placeholder_posters()
    
    print(f'\n✓ Cleanup Complete!')
    print(f'  📽️  Movies removed: {result["removed"]}')
    print(f'  ⭐ Ratings deleted: {result["ratings_removed"]}')
    print(f'  📋 Watchlist items deleted: {result["watchlist_removed"]}')
    
    if 'error' in result:
        print(f'\n❌ Error: {result["error"]}')
