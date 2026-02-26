#!/usr/bin/env python3
"""
Backfill and improve movie poster URLs for all movies.
Uses TMDB posters when possible and deterministic placeholders as fallback.
"""
from app import create_app, db
from app.models import Movie
from app.services.posters import get_poster_for_movie, get_tmdb_public_poster_url, get_tmdb_search_poster_url
from urllib.parse import quote_plus
import os
import requests


ITUNES_POSTER_CACHE = {}
ITUNES_FAILURES = 0
ITUNES_DISABLED = os.environ.get('USE_ITUNES_POSTERS', '0') != '1'
ITUNES_LOOKUPS = 0
MAX_ITUNES_LOOKUPS = 20


def is_synthetic_title(title):
    """Detect generated titles unlikely to have real posters."""
    value = (title or '').strip().lower()
    return '(2023 edition)' in value or value.endswith(' special') or ' v' in value


def fetch_tmdb_poster_path(movie, app, cache):
    """Get poster path from TMDB API for a movie's tmdb_id."""
    tmdb_id = movie.tmdb_id
    if not tmdb_id:
        return None

    if tmdb_id in cache:
        return cache[tmdb_id]

    api_key = app.config.get('TMDB_API_KEY')
    if not api_key:
        cache[tmdb_id] = None
        return None

    try:
        response = requests.get(
            f"{app.config.get('TMDB_BASE_URL', 'https://api.themoviedb.org/3')}/movie/{tmdb_id}",
            params={'api_key': api_key, 'language': 'en-US'},
            timeout=6,
        )
        response.raise_for_status()
        poster_path = response.json().get('poster_path')
        cache[tmdb_id] = poster_path
        return poster_path
    except Exception:
        cache[tmdb_id] = None
        return None


def build_placeholder(movie):
    """Build deterministic fallback poster URL."""
    return (
        f"https://placehold.co/500x750/1f2937/f8fafc?text="
        f"{quote_plus(movie.title or 'Untitled')}+({movie.year or 'Unknown'})"
    )


def fetch_itunes_poster_url(movie):
    """Fetch poster from iTunes Search API (no key required)."""
    global ITUNES_FAILURES, ITUNES_DISABLED, ITUNES_LOOKUPS

    normalized_title = (movie.title or '').strip().lower()
    if (
        ITUNES_DISABLED
        or ITUNES_LOOKUPS >= MAX_ITUNES_LOOKUPS
        or not normalized_title
        or is_synthetic_title(normalized_title)
    ):
        return None

    cache_key = normalized_title
    if cache_key in ITUNES_POSTER_CACHE:
        return ITUNES_POSTER_CACHE[cache_key]

    try:
        ITUNES_LOOKUPS += 1
        response = requests.get(
            'https://itunes.apple.com/search',
            params={
                'term': movie.title,
                'media': 'movie',
                'entity': 'movie',
                'limit': 10,
                'country': 'US',
            },
            timeout=(0.6, 1.2),
        )
        response.raise_for_status()
        ITUNES_FAILURES = 0
        results = response.json().get('results', [])

        best_url = None
        for result in results:
            result_title = (result.get('trackName') or '').strip().lower()
            if result_title != normalized_title:
                continue

            release_date = result.get('releaseDate', '')
            result_year = None
            if release_date and len(release_date) >= 4:
                try:
                    result_year = int(release_date[:4])
                except ValueError:
                    result_year = None

            if movie.year and result_year and movie.year != result_year:
                continue

            artwork = result.get('artworkUrl100') or result.get('artworkUrl60')
            if artwork:
                best_url = artwork.replace('100x100bb.jpg', '600x900bb.jpg').replace('60x60bb.jpg', '600x900bb.jpg')
                break

        ITUNES_POSTER_CACHE[cache_key] = best_url
        return best_url
    except Exception:
        ITUNES_FAILURES += 1
        if ITUNES_FAILURES >= 3:
            ITUNES_DISABLED = True
        ITUNES_POSTER_CACHE[cache_key] = None
        return None


def resolve_poster_url(movie, app, cache):
    """Resolve best poster URL for a movie record."""
    poster_path = fetch_tmdb_poster_path(movie, app, cache)
    if poster_path:
        image_base_url = app.config.get('TMDB_IMAGE_BASE_URL', 'https://image.tmdb.org/t/p/w500')
        return f"{image_base_url}{poster_path}"

    public_tmdb_poster = get_tmdb_public_poster_url(movie.tmdb_id)
    if public_tmdb_poster:
        return public_tmdb_poster

    if not is_synthetic_title(movie.title):
        search_tmdb_poster = get_tmdb_search_poster_url(movie.title)
        if search_tmdb_poster:
            return search_tmdb_poster

    itunes_poster = fetch_itunes_poster_url(movie)
    if itunes_poster:
        return itunes_poster

    known_or_placeholder = get_poster_for_movie(movie.title, movie.year)
    if known_or_placeholder:
        return known_or_placeholder

    return build_placeholder(movie)


def update_posters():
    """Update all movie posters using TMDB-first strategy."""
    app = create_app('development')

    with app.app_context():
        movies = Movie.query.all()
        total = len(movies)

        print(f"Updating {total} movie posters (TMDB + fallback)...")
        print("=" * 60)

        tmdb_cache = {}
        updated = 0
        unchanged = 0

        for idx, movie in enumerate(movies, 1):
            new_url = resolve_poster_url(movie, app, tmdb_cache)
            if movie.poster_url != new_url:
                movie.poster_url = new_url
                updated += 1
            else:
                unchanged += 1

            if idx % 100 == 0:
                print(f"  Updated {idx} movies...")

        # Commit all changes
        db.session.commit()

        print("\n✓ Successfully updated all movie posters!")
        print(f"✓ Changed posters: {updated}")
        print(f"✓ Unchanged posters: {unchanged}")
        print(f"✓ Total movies processed: {total}")
        print("\n✓ Sample posters:")
        for movie in Movie.query.limit(5).all():
            print(f"  - {movie.title}")
            print(f"    Poster: {movie.poster_url}")

        print("\n" + "=" * 60)
        print("Done! Refresh your browser to see new posters.\n")


if __name__ == '__main__':
    update_posters()
