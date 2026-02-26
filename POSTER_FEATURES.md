# Movie Poster Features

## Overview

The movie application now includes comprehensive poster management capabilities. All movies automatically get either real posters from TMDB or placeholder posters on startup.

## Features

### 1. Automatic Poster Assignment
- **On Startup**: When the app initializes, all movies without posters are assigned unique placeholder posters
- **Placeholder Format**: `https://placehold.co/500x750/1f2937/f8fafc?text=Movie+Title+Year`
- **Known Movies**: Popular movies like "The Shawshank Redemption", "The Dark Knight", etc. get real TMDB posters

### 2. Poster Management Features

#### Sync Posters
```bash
flask sync_posters
```
- Removes duplicate movies
- Assigns posters to movies missing them
- Fixes duplicate poster URLs

#### Fetch Missing Posters from TMDB
```bash
flask fetch_posters
```
- Fetches real posters from TMDB API for all movies without posters
- Requires `TMDB_API_KEY` in `.env`
- Searches by title/year if TMDB ID not available
- Falls back to placeholder if TMDB search fails

#### Update All Posters
```bash
flask update_posters
```
- Updates posters for all movies
- Uses existing posters if available, fetches new ones from TMDB

#### Force Re-fetch All Posters
```bash
flask update_posters --force
```
- Forces re-fetch of ALL posters from TMDB
- Useful for updating to newer/better poster versions

## Configuration

### TMDB API Setup

To fetch real posters from TMDB:

1. **Get API Key**:
   - Go to https://www.themoviedb.org/settings/api
   - Create an API key (requires free account)

2. **Add to `.env`**:
   ```
   TMDB_API_KEY=your_api_key_here
   ```

3. **Run Fetch Command**:
   ```bash
   flask fetch_posters
   ```

## How It Works

### Poster Resolution Order
For each movie, the system tries to find a poster in this order:

1. **Known Posters**: Check hardcoded list of popular movies
2. **TMDB by ID**: If movie has `tmdb_id`, fetch from TMDB
3. **TMDB by Search**: Search TMDB using title + year
4. **Placeholder**: Create unique placeholder using title + year

### Poster Sources
- **TMDB**: Real posters from The Movie Database (requires API key)
- **Placeholders**: Generated via placehold.co service

### Display
- Movies display their poster in list views, detail pages, and search results
- If no poster available, shows a generic image icon with fallback styling

## Poster Database Fields

```python
Movie.poster_url: String(500)    # URL to poster image
Movie.tmdb_id: Integer           # TMDB movie ID for API integration
```

## Examples

### Adding Movie with Poster
```python
# Movie is automatically assigned a poster on creation
movie = Movie(
    title='My Movie',
    description='...',
    year=2024,
    poster_url=None  # Auto-assigned by sync_movie_posters()
)
db.session.add(movie)
db.session.commit()
```

### Fetching Posters Programmatically
```python
from app.services.posters import fetch_missing_posters, update_all_movie_posters

# Fetch posters for movies without them
result = fetch_missing_posters()
print(f"Fetched: {result['fetched']}, Failed: {result['failed']}")

# Update all posters (force re-fetch)
result = update_all_movie_posters(force=True)
```

## Troubleshooting

### No TMDB_API_KEY Warning
If you see this warning:
```
⚠️  Warning: TMDB_API_KEY not configured in .env
```
- Add your TMDB API key to `.env` file
- Restart the app

### Slow Poster Fetching
- TMDB API has rate limits (40 requests/10 seconds)
- First-time fetch of many movies may take several minutes
- Consider running during off-peak hours

### Duplicate Poster URLs
Run this to fix:
```bash
flask sync_posters
```

### All Posters Are Placeholders
- TMDB API key not configured
- Add key to `.env` and run `flask fetch_posters`
- Check TMDB API key validity at https://www.themoviedb.org/settings/api

## Performance Notes

- Placeholder generation is instant (local, no API calls)
- TMDB API calls are cached to avoid duplicate requests
- Poster URLs are stored in database for fast retrieval
- Background updates don't block the web app

## File Structure

```
app/services/posters.py
├── KNOWN_POSTERS - Dict of hardcoded poster URLs
├── get_poster_for_movie() - Get poster or placeholder
├── sync_movie_posters() - Sync existing posters
├── fetch_missing_posters() - Fetch from TMDB
└── update_all_movie_posters() - Update all posters

run.py
├── @app.cli.command('sync_posters')
├── @app.cli.command('fetch_posters')
└── @app.cli.command('update_posters')
```

## Future Enhancements

Possible improvements:
- Background job for periodic poster updates
- Cache TMDB responses to reduce API calls
- Support for multiple poster sizes
- User-uploaded custom posters
- Poster quality/rating system
