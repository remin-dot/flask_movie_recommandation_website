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


def remove_movies_with_placeholder_posters():
    """
    Remove movies that have only placeholder posters (not real TMDB posters).
    
    A placeholder poster is one from placehold.co (temporary placeholder image).
    This function removes such movies along with their ratings and watchlist entries.
    
    Returns:
        Dictionary with removal statistics:
        - removed: Number of movies removed
        - ratings_removed: Number of associated ratings deleted
        - watchlist_removed: Number of watchlist items deleted
    """
    # Find all movies with placeholder posters
    movies_with_placeholders = Movie.query.filter(
        Movie.poster_url.like('%placehold.co%')
    ).all()
    
    removed_count = 0
    ratings_removed = 0
    watchlist_removed = 0
    
    logger.info(f"Found {len(movies_with_placeholders)} movies with placeholder posters")
    
    for movie in movies_with_placeholders:
        try:
            # Delete associated ratings
            ratings = Rating.query.filter_by(movie_id=movie.id).all()
            for rating in ratings:
                db.session.delete(rating)
                ratings_removed += 1
            
            # Delete associated watchlist items
            watchlist_items = Watchlist.query.filter_by(movie_id=movie.id).all()
            for item in watchlist_items:
                db.session.delete(item)
                watchlist_removed += 1
            
            # Delete the movie itself
            db.session.delete(movie)
            removed_count += 1
            
            logger.info(f"Removed movie with placeholder poster: '{movie.title}' (ID: {movie.id})")
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error removing movie {movie.id} ('{movie.title}'): {e}")
    
    # Commit all deletions
    if removed_count > 0:
        try:
            db.session.commit()
            logger.info(f"Successfully removed {removed_count} movies with placeholder posters")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to commit deletions: {e}")
            return {
                'removed': 0,
                'ratings_removed': 0,
                'watchlist_removed': 0,
                'error': str(e)
            }
    
    return {
        'removed': removed_count,
        'ratings_removed': ratings_removed,
        'watchlist_removed': watchlist_removed
    }


def clean_movie_data():
    """Normalize movie titles and years, strip HTML and whitespace.

    Returns the number of movies modified.
    """
    import re

    changed = 0
    movies = Movie.query.all()
    for movie in movies:
        orig_title = movie.title or ''
        # remove HTML tags/unsafe characters and collapse spaces
        cleaned = re.sub(r'<[^>]+>', '', orig_title)
        cleaned = ''.join(ch for ch in cleaned if ch.isprintable())
        cleaned = cleaned.strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if cleaned != orig_title:
            movie.title = cleaned
            changed += 1

        # ensure year is integer
        if movie.year is not None and not isinstance(movie.year, int):
            try:
                movie.year = int(movie.year)
                changed += 1
            except (ValueError, TypeError):
                pass

    if changed:
        db.session.commit()
    return changed

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


def _is_real_poster_url(url):
    """Return True if the URL appears to be a real TMDB poster/image."""
    if not url:
        return False
    url = url.lower()
    return 'image.tmdb.org' in url or 'media.themoviedb.org' in url


def _normalize_title_for_match(title):
    """Normalize title for fuzzy-ish matching: lowercase, remove punctuation and extra tokens."""
    if not title:
        return ''
    s = re.sub(r'[^a-z0-9\s]', ' ', title.lower())
    s = re.sub(r'\s+', ' ', s).strip()
    # Remove common noise tokens like edition markers
    s = re.sub(r'edition \d+', '', s)
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'\b(ed|edition)\b', '', s)
    s = re.sub(r'\d{3,}', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def _title_similarity(a, b):
    """Simple token overlap similarity between two normalized titles."""
    a_tokens = set(a.split())
    b_tokens = set(b.split())
    if not a_tokens or not b_tokens:
        return 0.0
    inter = a_tokens.intersection(b_tokens)
    return len(inter) / max(len(a_tokens), len(b_tokens))


def enrich_missing_posters_aggressively(max_pages=3):
    """
    Try harder to find real TMDB posters for movies that currently lack TMDB images.

    Strategy:
    - Skip movies that already have a real TMDB poster URL
    - Try searching TMDB by several title variations and up to `max_pages` pages
    - Use a lightweight token-similarity heuristic to accept matches
    - Update `tmdb_id` and `poster_url` when a real poster is found
    """
    from flask import current_app

    api_key = current_app.config.get('TMDB_API_KEY', '').strip()
    if not api_key:
        logger.warning('TMDB API key not configured; aggressive enrichment skipped')
        return {'total': 0, 'fetched': 0}

    movies = Movie.query.all()
    total = 0
    fetched = 0

    for movie in movies:
        url = (movie.poster_url or '').strip()
        if _is_real_poster_url(url):
            continue

        total += 1
        title = movie.title or ''
        year = movie.year

        candidates = []

        # Build title variations
        variations = [title]
        # remove parenthetical parts
        v2 = re.sub(r'\(.*?\)', '', title).strip()
        if v2 and v2 != title:
            variations.append(v2)
        # remove edition tokens like "Edition 499"
        v3 = re.sub(r'edition\s*\d+', '', title, flags=re.I).strip()
        if v3 and v3 not in variations:
            variations.append(v3)
        # try title without trailing numbers
        v4 = re.sub(r'\s+\(?(edition\s*)?\d+\)?$', '', title, flags=re.I).strip()
        if v4 and v4 not in variations:
            variations.append(v4)

        norm_target = _normalize_title_for_match(title)

        found = False
        for var in variations:
            if found:
                break
            for page in range(1, max_pages + 1):
                tmdb_id, poster_url = search_tmdb_posters_by_title(var, year if page == 1 else None, api_key=api_key)
                # If search returns a tmdb_id but no poster, try getting details
                if tmdb_id and not poster_url:
                    poster_url = fetch_tmdb_poster_by_id(tmdb_id)

                if not tmdb_id and not poster_url:
                    # try next page with no year
                    continue

                # Validate candidate by fetching details and comparing titles
                try:
                    if tmdb_id:
                        details = None
                        try:
                            from app.services.tmdb import TMDBService
                            svc = TMDBService()
                            details = svc.get_movie_details(tmdb_id)
                        except Exception:
                            details = None

                        candidate_title = (details.get('title') if details else None) or var
                    else:
                        candidate_title = var

                    norm_candidate = _normalize_title_for_match(candidate_title)
                    sim = _title_similarity(norm_target, norm_candidate)
                    # Accept if similarity high enough or poster_url clearly from TMDB
                    if sim >= 0.5 or (poster_url and _is_real_poster_url(poster_url)):
                        # Accept this poster
                        movie.poster_url = poster_url or build_unique_placeholder(movie.title, movie.year)
                        if tmdb_id:
                            existing = Movie.query.filter(Movie.tmdb_id==tmdb_id).first()
                            if existing and existing.id != movie.id:
                                logger.debug(f"TMDB id {tmdb_id} already assigned to movie id {existing.id}; skipping tmdb_id assignment for '{movie.title}'")
                            elif not movie.tmdb_id:
                                movie.tmdb_id = tmdb_id
                        db.session.add(movie)
                        try:
                            db.session.commit()
                        except Exception as e:
                            db.session.rollback()
                            logger.warning(f"Commit failed when enriching '{movie.title}' (tmdb_id={tmdb_id}): {e}; saving poster_url only")
                            try:
                                m2 = Movie.query.get(movie.id)
                                if m2:
                                    m2.poster_url = movie.poster_url
                                    db.session.add(m2)
                                    db.session.commit()
                                    fetched += 1
                            except Exception as e2:
                                db.session.rollback()
                                logger.debug(f"Failed to persist poster_url-only for '{movie.title}': {e2}")
                        else:
                            fetched += 1
                        found = True
                        logger.info(f"Enriched poster for '{movie.title}' with tmdb_id={tmdb_id}")
                        break
                except Exception as e:
                    logger.debug(f"Error validating TMDB candidate for '{movie.title}': {e}")

    logger.info(f"Aggressive enrichment complete: scanned={total}, fetched={fetched}")
    return {'total': total, 'fetched': fetched}


def sync_movie_details_with_tmdb():
    """
    Synchronize movie titles, descriptions, and details with TMDB data.
    
    For each movie with a poster or TMDB ID, fetch the correct information from TMDB
    and update the database to ensure data consistency with the poster.
    
    Returns:
        Dictionary with synchronization statistics:
        - total: Total movies processed
        - updated: Movies with changes
        - unchanged: Movies with no changes
        - failed: Movies that couldn't be synced
    """
    from flask import current_app
    from app.models import Genre
    from app.services.tmdb import TMDBService
    
    api_key = current_app.config.get('TMDB_API_KEY', '').strip()
    if not api_key:
        logger.warning('TMDB API key not configured; detail sync skipped')
        return {'total': 0, 'updated': 0, 'unchanged': 0, 'failed': 0}
    
    # Get all movies with a TMDB ID or a real poster URL
    movies = Movie.query.filter(
        db.or_(
            Movie.tmdb_id != None,
            Movie.poster_url.like('%image.tmdb.org%'),
            Movie.poster_url.like('%media.themoviedb.org%')
        )
    ).all()
    
    total = len(movies)
    updated = 0
    unchanged = 0
    failed = 0
    
    logger.info(f"Starting to sync {total} movies with TMDB data")
    
    tmdb_service = TMDBService()
    
    for movie in movies:
        tmdb_id = movie.tmdb_id
        
        # If no tmdb_id but has real poster, try to search for it
        if not tmdb_id and _is_real_poster_url(movie.poster_url or ''):
            try:
                tmdb_id, _ = search_tmdb_posters_by_title(movie.title, movie.year, api_key=api_key)
            except Exception as e:
                logger.debug(f"Failed to find TMDB ID for '{movie.title}': {e}")
                failed += 1
                continue
        
        if not tmdb_id:
            unchanged += 1
            continue
        
        try:
            # Fetch full details from TMDB
            details = tmdb_service.get_movie_details(tmdb_id)
            if not details:
                logger.debug(f"Could not fetch details for TMDB ID {tmdb_id}")
                failed += 1
                continue
            
            # Track if we made changes
            made_changes = False
            
            # Update title if different
            tmdb_title = details.get('title', '').strip()
            if tmdb_title and tmdb_title != movie.title:
                logger.debug(f"Updating title for movie {movie.id}: '{movie.title}' -> '{tmdb_title}'")
                movie.title = tmdb_title
                made_changes = True
            
            # Update description if different or missing
            tmdb_description = details.get('overview', '').strip()
            if tmdb_description:
                current_desc = (movie.description or '').strip()
                if not current_desc or tmdb_description != current_desc:
                    logger.debug(f"Updating description for movie {movie.id}")
                    movie.description = tmdb_description
                    made_changes = True
            elif not movie.description:
                # If we have no description and TMDB has none, set a default
                movie.description = 'No description available'
                made_changes = True
            
            # Update year if it exists in TMDB
            release_date = details.get('release_date', '').strip()
            if release_date:
                try:
                    tmdb_year = int(release_date.split('-')[0])
                    if tmdb_year and tmdb_year != movie.year:
                        logger.debug(f"Updating year for movie {movie.id}: {movie.year} -> {tmdb_year}")
                        movie.year = tmdb_year
                        made_changes = True
                except (ValueError, IndexError):
                    pass
            
            # Update poster URL if we found one and it's different
            poster_path = details.get('poster_path')
            if poster_path:
                tmdb_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                if tmdb_poster_url != movie.poster_url:
                    logger.debug(f"Updating poster URL for movie {movie.id}")
                    movie.poster_url = tmdb_poster_url
                    made_changes = True
            
            # Update genres
            if details.get('genres'):
                tmdb_genre_names = {g.get('name') for g in details['genres'] if g.get('name')}
                current_genre_names = {g.name for g in movie.genres}
                
                if tmdb_genre_names != current_genre_names:
                    # Remove genres that are no longer in TMDB data
                    for genre in list(movie.genres):
                        if genre.name not in tmdb_genre_names:
                            movie.genres.remove(genre)
                    
                    # Add new genres from TMDB
                    for genre_name in tmdb_genre_names:
                        if not any(g.name == genre_name for g in movie.genres):
                            genre = Genre.query.filter_by(name=genre_name).first()
                            if not genre:
                                genre = Genre(name=genre_name)
                                db.session.add(genre)
                            movie.genres.append(genre)
                    
                    made_changes = True
            
            # Commit changes if any were made
            if made_changes:
                if not movie.tmdb_id:
                    movie.tmdb_id = tmdb_id
                db.session.add(movie)
                db.session.commit()
                updated += 1
                logger.info(f"Synced movie {movie.id}: '{movie.title}'")
            else:
                unchanged += 1
        
        except Exception as e:
            logger.error(f"Failed to sync movie {movie.id} (TMDB ID {tmdb_id}): {e}")
            db.session.rollback()
            failed += 1
    
    logger.info(f"Sync complete: {updated} updated, {unchanged} unchanged, {failed} failed")
    
    return {
        'total': total,
        'updated': updated,
        'unchanged': unchanged,
        'failed': failed
    }