"""
Script to force-fetch all TMDB posters for all movies
"""

from app import create_app
from app.services.posters import update_all_movie_posters

app = create_app()
with app.app_context():
    print('Force-fetching all TMDB posters for all movies...')
    print('This may take a moment (respect API rate limits)...')
    print('')
    result = update_all_movie_posters(force=True)
    print('')
    print('✓ Poster update complete!')
    print(f'  Total movies: {result["total"]}')
    print(f'  Updated: {result["updated"]}')
    print(f'  Unchanged: {result["kept"]}')
