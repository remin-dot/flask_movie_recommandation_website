# Movie Details Synchronization with TMDB

## Overview

This feature synchronizes movie information (titles, descriptions, genres, release years) with TMDB (The Movie Database) data associated with movie posters. This ensures data consistency and accuracy across your movie collection.

## ทำไมต้องซิงค์ข้อมูล? (Why Synchronize?)

When you fetch movie posters from TMDB, sometimes the associated movie information in your database may:
- Have incorrect titles (e.g., abbreviations, transliterations)
- Missing or outdated descriptions
- Wrong release years
- Incomplete or missing genre information

The synchronization feature fixes these issues by updating your local database with the authoritative data from TMDB.

## วิธีการทำงาน (How It Works)

1. **Identifies Movies**: Finds all movies with TMDB IDs or real TMDB posters
2. **Fetches Data**: Retrieves complete movie details from TMDB API
3. **Updates Locally**: Updates titles, descriptions, years, and genres in your database
4. **Preserves Data**: Keeps user ratings and watchlist items intact
5. **Reports Results**: Shows statistics on what was updated

## ใช้ Sync Script (Using Command Line)

### ตัวเลือก 1: Standalone Script
```bash
# Navigate to project directory
cd /path/to/project

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Run the sync script
python sync_movie_details.py

# Expected output:
# Synchronizing movie details with TMDB data...
# This may take a few moments...
#
# ✓ Synchronization Complete!
#   Total movies processed: 500
#   ✓ Updated: 123
#   → Unchanged: 347
#   ✗ Failed: 30
```

### ตัวเลือก 2: Admin Panel
1. Login as administrator
2. Go to **Admin Panel** → **Admin Dashboard**
3. Click on **Sync Movie Details**
4. Click **Start Sync**
5. Wait for completion and review the results

## ข้อมูลที่ได้รับการอัพเดต (Updated Information)

The synchronization updates the following fields for each movie:

### ✓ Movie Title
- **Before**: "Kingsman" 
- **After**: "Kingsman: The Secret Service"
- Ensures full, accurate titles from TMDB

### ✓ Description/Overview
- Updates movie plot summary from TMDB
- Provides consistent, professionally-written descriptions
- Uses English descriptions (can be translated later)

### ✓ Release Year
- Corrects incorrect years in your database
- Uses official release date from TMDB
- Example: Year 2015 → Year 2015 (after correction)

### ✓ Genres
- Syncs genres with TMDB's official genre list
- Removes obsolete or incorrect genres
- Adds missing genre associations

### ✓ TMDB ID
- Automatically links movies to their TMDB record
- Enables future TMDB integrations
- Prevents duplicate TMDB lookups

## การออกแบบข้อมูล (Data Preservation)

**The synchronization DOES NOT affect:**
- ✓ User ratings and reviews
- ✓ Watchlist items
- ✓ User accounts
- ✓ Site configuration
- ✓ Custom poster URLs (only real TMDB posters)

**The synchronization UPDATES:**
- Movie titles
- Movie descriptions
- Release years
- Genre associations
- TMDB IDs

## ตัวอย่างผลลัพธ์ (Example Results)

```
Movie 1: "The Dark Knight" → "The Dark Knight" (unchanged)
  - Already has correct information
  - TMDB ID linked

Movie 2: "Kingsman" → "Kingsman: The Secret Service"
  - Title completed with full subtitle
  - Description updated with official synopsis
  - Year verified: 2015

Movie 3: "Fast 7" → "Furious 7"
  - Title corrected to official name
  - Description updated
  - Genres synced with TMDB

Statistics:
- Total movies processed: 500
- Updated: 147 (29.4%)
- Unchanged: 322 (64.4%)
- Failed: 31 (6.2%)
```

## เมื่อการซิงค์ล้มเหลว (When Sync Fails)

A movie sync fails when:

1. **Can't find TMDB match**
   - Movie title too obscure or misspelled
   - No TMDB ID in database
   - Movie not on TMDB

2. **API errors**
   - TMDB API temporarily unavailable
   - Network connection issues
   - Rate limit exceeded

3. **Data conflicts**
   - Multiple TMDB movies match one title
   - Insufficient data for confident matching

**What happens**: 
- Failed movies are skipped
- Their current data is preserved safely
- Detailed logs show which movies failed
- You can manually correct these later

## การแก้ไขข้อมูลด้วยตนเอง (Manual Corrections)

For failed or incorrect sync results:

### Via Admin Panel:
1. Go to **Admin Panel** → **Manage Movies**
2. Click on a movie to edit
3. Update fields as needed
4. Save changes

### Via Database (Advanced):
```sql
-- Update a specific movie
UPDATE movies 
SET title = 'Correct Title', 
    description = 'Correct description...',
    year = 2024,
    tmdb_id = 12345
WHERE id = 1;
```

## เอการซิงค์ใหม่ (Running Sync Again)

You can safely run the sync multiple times:

- **Idempotent**: Running twice won't duplicate changes
- **Safe**: Only updates if data differs from TMDB
- **Efficient**: Skips already-correct movies
- **Recommended**: Run monthly to catch TMDB updates

```bash
# Schedule with cron (Linux/Mac)
0 2 * * 1 cd /path/to/project && python sync_movie_details.py > logs/sync.log 2>&1

# Or use Windows Task Scheduler
# Run: python sync_movie_details.py
# Schedule: Weekly (e.g., Monday 2 AM)
```

## จำนวนสถานการณ์ (Common Scenarios)

### Scenario 1: Initial Setup
```
First sync after importing 1000 movies:
- Many movies have placeholder data
- Expected: 60-70% updated, 30-40% unchanged/failed
- Action: Review failed movies, consider manual corrections
```

### Scenario 2: Regular Maintenance
```
Monthly sync of established database:
- Most movies already synced
- Expected: 5-10% updated, 85-90% unchanged
- Action: Review any new updates, verify accuracy
```

### Scenario 3: Missing Descriptions
```
All movies have titles/years but missing descriptions:
- Expected: 70-80% descriptions added
- Action: Verify descriptions look correct
```

## ปัญหาและการแก้ไข (Troubleshooting)

### Problem: "TMDB API key not configured"
**Solution**: 
```bash
# Check .env file
cat .env | grep TMDB_API_KEY

# Should output: TMDB_API_KEY=your_key_here
# If not configured, add it to .env and restart
```

### Problem: Sync takes too long
**Solution**:
- TMDB API has rate limits (40 requests/10 seconds)
- This is normal for large databases
- Expected time: ~2-5 seconds per 100 movies
- Don't interrupt the process

### Problem: Wrong movies got updated
**Solution**:
- Check TMDB IDs in database - they may be incorrect
- Review `logs/app.log` for detailed sync logs
- Consider running sync again after fixing TMDB IDs
- Use manual corrections for specific movies

### Problem: Sync failed for all movies
**Solution**:
1. Verify TMDB_API_KEY is set: `python -c "from flask import current_app; print(current_app.config.get('TMDB_API_KEY'))"`
2. Check network connection
3. Try again in a few minutes (API might be rate-limited)
4. Check error logs: `tail -f logs/app.log`

## API ข้อมูล (API Reference)

### Python Function
```python
from app.services.posters import sync_movie_details_with_tmdb

result = sync_movie_details_with_tmdb()
# Returns: {'total': 500, 'updated': 123, 'unchanged': 347, 'failed': 30}
```

### Required Configuration
```python
# In config.py or .env
TMDB_API_KEY = 'your_tmdb_api_key'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'
TMDB_IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
```

### Performance Notes
- Processes movies sequentially 
- Average: 0.5-1 second per movie
- Total time: 5-15 minutes for 500 movies
- Uses SQLAlchemy ORM for safe database operations

## Best Practices

1. **Backup Before Large Syncs**
   ```bash
   # SQLite backup
   cp instance/app.db instance/app.db.backup

   # PostgreSQL backup
   pg_dump your_database > backup.sql
   ```

2. **Review Results**
   - Always check the sync report
   - Review any failed movies
   - Spot-check a few updated titles

3. **Schedule Regular Syncs**
   - Monthly is recommended
   - TMDB updates frequently
   - Keeps database fresh and accurate

4. **Monitor Logs**
   ```bash
   tail -f logs/app.log | grep "sync_movie_details"
   ```

5. **Use with Poster Enrichment**
   - Run `python run_enrich_posters.py` first
   - Then run sync to update titles/descriptions
   - Ensures complete movie information

## สรุป (Summary)

The movie details synchronization feature:

✓ **Ensures Data Consistency**: Titles, descriptions, and info match TMDB
✓ **Preserves User Data**: Ratings, reviews, and watchlists stay intact
✓ **Easy to Use**: One command or button click
✓ **Safe**: Idempotent, can run multiple times
✓ **Tracked**: Detailed logs and statistics
✓ **Customizable**: Can manually correct any issues

For questions or issues, check the application logs or contact support.

---

**Last Updated**: February 26, 2026
**Version**: 1.0
**Language Support**: English, Thai, Japanese, Chinese, Spanish
