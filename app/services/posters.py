"""
Poster utilities for movie records.
Ensures each movie has a poster URL and fixes duplicate poster URLs.
"""

import os
import re
import requests
import logging
from urllib.parse import quote_plus, quote_plus as url_quote_plus
from sqlalchemy import inspect, text
from app.models import db, Movie, Rating, Watchlist

logger = logging.getLogger(__name__)


KNOWN_POSTERS = {
    'the shawshank redemption': 'https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg',
    'the dark knight': 'https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg',
    'inception': 'https://image.tmdb.org/t/p/w500/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg',
    'dune': 'https://image.tmdb.org/t/p/w500/d5NXSklXo0qyIYkgV94XAgMIckC.jpg',
    'the grand budapest hotel': 'https://image.tmdb.org/t/p/w500/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg',
    'parasite': 'https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg',
    'avatar': 'https://image.tmdb.org/t/p/w500/kyeqWdyUXW608qlYkRqosgbbJyK.jpg',
    'pulp fiction': 'https://image.tmdb.org/t/p/w500/vQWk5YBFWF4bZaofAbv0tShwBvQ.jpg',
    'forrest gump': 'https://image.tmdb.org/t/p/w500/arw2vcBveWOVZr6pxd9XTd1TdQa.jpg',
    'interstellar': 'https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
}

TMDB_PUBLIC_POSTER_CACHE = {}
TMDB_PUBLIC_FAILURES = 0
TMDB_PUBLIC_DISABLED = False
TMDB_SEARCH_POSTER_CACHE = {}
TMDB_SEARCH_FAILURES = 0
TMDB_SEARCH_DISABLED = os.environ.get('USE_TMDB_SEARCH_POSTERS', '1') != '1'
TMDB_SEARCH_LOOKUPS = 0
MAX_TMDB_SEARCH_LOOKUPS = int(os.environ.get('MAX_TMDB_SEARCH_LOOKUPS', '120'))


def get_tmdb_public_poster_url(tmdb_id):
    """Fetch poster URL from public TMDB movie page without API key."""
    global TMDB_PUBLIC_FAILURES, TMDB_PUBLIC_DISABLED

    if not tmdb_id:
        return None

    if tmdb_id in TMDB_PUBLIC_POSTER_CACHE:
        return TMDB_PUBLIC_POSTER_CACHE[tmdb_id]

    if TMDB_PUBLIC_DISABLED:
        TMDB_PUBLIC_POSTER_CACHE[tmdb_id] = None
        return None


def _normalize_tmdb_media_url(candidate):
    """Normalize TMDB media URL to a stable w500 URL when possible."""
    if not candidate:
        return None

    filename_match = re.search(r'/([^/]+\.(?:jpg|jpeg|png|webp))(?:\?|$)', candidate, flags=re.IGNORECASE)
    if not filename_match:
        return candidate

    filename = filename_match.group(1)
    return f"https://media.themoviedb.org/t/p/w500/{filename}"


def get_tmdb_search_poster_url(title):
    """Fetch poster URL from TMDB public title search (no API key)."""
    global TMDB_SEARCH_FAILURES, TMDB_SEARCH_DISABLED, TMDB_SEARCH_LOOKUPS

    normalized_title = (title or '').strip().lower()
    if not normalized_title:
        return None

    if normalized_title in TMDB_SEARCH_POSTER_CACHE:
        return TMDB_SEARCH_POSTER_CACHE[normalized_title]

    if TMDB_SEARCH_DISABLED or TMDB_SEARCH_LOOKUPS >= MAX_TMDB_SEARCH_LOOKUPS:
        TMDB_SEARCH_POSTER_CACHE[normalized_title] = None
        return None

    try:
        TMDB_SEARCH_LOOKUPS += 1
        response = requests.get(
            f"https://www.themoviedb.org/search/movie?query={url_quote_plus(title)}",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=(0.8, 1.5),
        )
        response.raise_for_status()

        # Find first result card and poster source URL
        first_match = re.search(
            r'class="result"[^>]*href="/movie/\d+[^"]*"[^>]*>\s*<img[^>]+src="([^"]+)"',
            response.text,
            flags=re.IGNORECASE,
        )

        poster_url = _normalize_tmdb_media_url(first_match.group(1)) if first_match else None
        TMDB_SEARCH_POSTER_CACHE[normalized_title] = poster_url
        TMDB_SEARCH_FAILURES = 0
        return poster_url
    except Exception:
        TMDB_SEARCH_FAILURES += 1
        if TMDB_SEARCH_FAILURES >= 5:
            TMDB_SEARCH_DISABLED = True
        TMDB_SEARCH_POSTER_CACHE[normalized_title] = None
        return None

    try:
        response = requests.get(
            f"https://www.themoviedb.org/movie/{tmdb_id}",
            headers={'User-Agent': 'Mozilla/5.0'},
            timeout=(0.8, 1.5),
        )
        response.raise_for_status()

        match = re.search(r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', response.text, flags=re.IGNORECASE)
        poster_url = None
        if match:
            candidate = match.group(1).split('?')[0]
            if 'image.tmdb.org' in candidate or 'media.themoviedb.org' in candidate:
                poster_url = candidate

        TMDB_PUBLIC_POSTER_CACHE[tmdb_id] = poster_url
        TMDB_PUBLIC_FAILURES = 0
        return poster_url
    except Exception:
        TMDB_PUBLIC_FAILURES += 1
        if TMDB_PUBLIC_FAILURES >= 5:
            TMDB_PUBLIC_DISABLED = True
        TMDB_PUBLIC_POSTER_CACHE[tmdb_id] = None
        return None


def ensure_movie_schema():
    """Ensure legacy databases include poster_url column."""
    inspector = inspect(db.engine)
    movie_columns = {column['name'] for column in inspector.get_columns('movies')}

    if 'poster_url' not in movie_columns:
        db.session.execute(text('ALTER TABLE movies ADD COLUMN poster_url VARCHAR(500)'))
        db.session.commit()


def build_unique_placeholder(title, year, unique_suffix=None):
    """Build deterministic fallback poster URL unique to movie row."""
    suffix = f" #{unique_suffix}" if unique_suffix is not None else ""
    label = quote_plus(f"{title} ({year}){suffix}")
    return f"https://placehold.co/500x750/1f2937/f8fafc?text={label}"


def get_poster_for_movie(title, year):
    """Get poster URL from known set or fallback placeholder."""
    normalized_title = (title or '').strip().lower()
    known_poster = KNOWN_POSTERS.get(normalized_title)
    if known_poster:
        return known_poster
    return build_unique_placeholder(title, year)


def sync_movie_posters():
    """Assign missing posters and fix duplicate poster URLs."""
    movies = Movie.query.all()
    changed = 0

    for movie in movies:
        if not movie.poster_url:
            movie.poster_url = get_poster_for_movie(movie.title, movie.year)
            changed += 1

    seen_urls = {}
    duplicate_fixes = 0
    for movie in movies:
        url = (movie.poster_url or '').strip()
        if not url:
            movie.poster_url = get_poster_for_movie(movie.title, movie.year)
            changed += 1
            continue

        if url.startswith('/static/'):
            continue

        if url in seen_urls:
            movie.poster_url = build_unique_placeholder(movie.title, movie.year, unique_suffix=movie.id)
            duplicate_fixes += 1
            changed += 1
        else:
            seen_urls[url] = movie.id

    if changed:
        db.session.commit()

    return {
        'changed': changed,
        'duplicate_fixes': duplicate_fixes,
    }


def remove_duplicate_movies():
    """Remove duplicate movies by normalized title + year while preserving related records."""
    movies = Movie.query.order_by(Movie.id.asc()).all()
    groups = {}

    for movie in movies:
        key = ((movie.title or '').strip().lower(), movie.year)
        groups.setdefault(key, []).append(movie)

    removed_count = 0

    for duplicates in groups.values():
        if len(duplicates) <= 1:
            continue

        keeper = duplicates[0]
        duplicate_movies = duplicates[1:]

        for duplicate in duplicate_movies:
            duplicate_ratings = Rating.query.filter_by(movie_id=duplicate.id).all()
            for duplicate_rating in duplicate_ratings:
                keeper_rating = Rating.query.filter_by(
                    user_id=duplicate_rating.user_id,
                    movie_id=keeper.id
                ).first()

                if keeper_rating:
                    if duplicate_rating.rating > keeper_rating.rating:
                        keeper_rating.rating = duplicate_rating.rating
                    if not keeper_rating.review and duplicate_rating.review:
                        keeper_rating.review = duplicate_rating.review
                    db.session.delete(duplicate_rating)
                else:
                    duplicate_rating.movie_id = keeper.id

            duplicate_watchlist_items = Watchlist.query.filter_by(movie_id=duplicate.id).all()
            for duplicate_item in duplicate_watchlist_items:
                keeper_item = Watchlist.query.filter_by(
                    user_id=duplicate_item.user_id,
                    movie_id=keeper.id
                ).first()

                if keeper_item:
                    db.session.delete(duplicate_item)
                else:
                    duplicate_item.movie_id = keeper.id

            db.session.delete(duplicate)
            removed_count += 1

    if removed_count:
        db.session.commit()

    return removed_count

def fetch_tmdb_poster_by_id(tmdb_id):
    """
    Fetch poster directly from TMDB API using tmdb_id
    
    Args:
        tmdb_id: TMDB movie ID
    
    Returns:
        Poster URL or None if not found
    """
    try:
        from flask import current_app
        api_key = current_app.config.get('TMDB_API_KEY', '').strip()
        
        if not api_key or not tmdb_id:
            return None
        
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        params = {
            'api_key': api_key,
            'language': 'en-US'
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        poster_path = data.get('poster_path')
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        
        return None
    
    except Exception as e:
        logger.warning(f"Failed to fetch TMDB poster for tmdb_id {tmdb_id}: {str(e)}")
        return None


def search_tmdb_posters_by_title(title, year=None, api_key=None):
    """
    Search TMDB for a movie and fetch its poster
    
    Args:
        title: Movie title
        year: Release year (optional, improves accuracy)
        api_key: TMDB API key (uses config if not provided)
    
    Returns:
        Tuple (tmdb_id, poster_url) or (None, None) if not found
    """
    try:
        if not api_key:
            from flask import current_app
            api_key = current_app.config.get('TMDB_API_KEY', '').strip()
        
        if not api_key:
            return None, None
        
        # Search for movie
        search_url = "https://api.themoviedb.org/3/search/movie"
        search_params = {
            'api_key': api_key,
            'query': title,
            'language': 'en-US',
            'include_adult': False
        }
        
        if year:
            search_params['year'] = year
        
        search_response = requests.get(search_url, params=search_params, timeout=5)
        search_response.raise_for_status()
        
        results = search_response.json().get('results', [])
        
        if not results:
            logger.debug(f"No TMDB results for: {title}")
            return None, None
        
        # Get first result
        movie = results[0]
        tmdb_id = movie.get('id')
        poster_path = movie.get('poster_path')
        
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            return tmdb_id, poster_url
        
        return tmdb_id, None
    
    except Exception as e:
        logger.warning(f"Failed to search TMDB for '{title}': {str(e)}")
        return None, None


def fetch_missing_posters():
    """
    Fetch posters from TMDB API for all movies without posters
    
    Returns:
        Dictionary with statistics about posters fetched
    """
    movies = Movie.query.filter(
        db.or_(Movie.poster_url == None, Movie.poster_url == '')
    ).all()
    
    fetched = 0
    failed = 0
    
    logger.info(f"Fetching posters for {len(movies)} movies without posters")
    
    for movie in movies:
        poster_url = None
        
        # Try to fetch from TMDB using tmdb_id if available
        if movie.tmdb_id:
            poster_url = fetch_tmdb_poster_by_id(movie.tmdb_id)
        
        # If still no poster, search by title
        if not poster_url:
            tmdb_id, poster_url = search_tmdb_posters_by_title(movie.title, movie.year)
            
            # Update tmdb_id if we found one
            if tmdb_id and not movie.tmdb_id:
                movie.tmdb_id = tmdb_id
        
        # Use placeholder if still no poster
        if not poster_url:
            poster_url = build_unique_placeholder(movie.title, movie.year)
            failed += 1
        else:
            fetched += 1
        
        movie.poster_url = poster_url
    
    if movies:
        db.session.commit()
    
    logger.info(f"Poster fetch complete: {fetched} from TMDB, {failed} placeholders")
    
    return {
        'total': len(movies),
        'fetched': fetched,
        'failed': failed
    }


def update_all_movie_posters(force=False):
    """
    Update all movie posters, optionally forcing refresh
    
    Args:
        force: If True, re-fetch even existing posters
    
    Returns:
        Dictionary with update statistics
    """
    if force:
        movies = Movie.query.all()
    else:
        movies = Movie.query.filter(
            db.or_(Movie.poster_url == None, Movie.poster_url == '')
        ).all()
    
    logger.info(f"Updating posters for {len(movies)} movies (force={force})")
    
    updated = 0
    kept = 0
    
    for movie in movies:
        old_poster = movie.poster_url
        
        # Try TMDB if available
        if movie.tmdb_id:
            poster_url = fetch_tmdb_poster_by_id(movie.tmdb_id)
        else:
            # Try searching
            tmdb_id, poster_url = search_tmdb_posters_by_title(movie.title, movie.year)
            if tmdb_id:
                movie.tmdb_id = tmdb_id
        
        # Use placeholder if needed
        if not poster_url:
            # Check for known posters first
            normalized_title = movie.title.lower().strip()
            poster_url = KNOWN_POSTERS.get(normalized_title)
        
        if not poster_url:
            poster_url = build_unique_placeholder(movie.title, movie.year)
        
        movie.poster_url = poster_url
        
        if old_poster != poster_url:
            updated += 1
        else:
            kept += 1
    
    if movies:
        db.session.commit()
    
    logger.info(f"Poster update complete: {updated} updated, {kept} unchanged")
    
    return {
        'total': len(movies),
        'updated': updated,
        'kept': kept
    }