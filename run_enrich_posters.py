"""
Helper script to run aggressive poster enrichment
"""
from dotenv import load_dotenv
import os

# Load environment variables from .env so TMDB_API_KEY is available
load_dotenv()
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
from app.services.posters import enrich_missing_posters_aggressively

app = create_app()
with app.app_context():
    print('Running aggressive poster enrichment (this may take a while)...')
    result = enrich_missing_posters_aggressively(max_pages=4)
    print('Done.')
    print(f"Scanned: {result['total']}, Fetched: {result['fetched']}")
