# 🗑️ Remove Placeholder Movies - Quick Reference

## Fastest Way to Remove Placeholder Movies

### Option 1: Command Line (30 seconds)
```bash
python remove_placeholder_movies.py
```
Then answer "yes" to confirm.

### Option 2: Admin Panel (1 minute)
1. Login as admin
2. Dashboard → Remove Placeholder Movies
3. Click button, confirm twice

---

## What Gets Deleted

✕ Movies with `placehold.co` posters only  
✕ Their ratings  
✕ Their watchlist items  

✓ Everything else is safe

---

## Example

**Before:**
```
Movie "The Matrix" - placehold.co/... poster ✕
Movie "Avatar" - TMDB real poster ✓
Movie "Inception" - placehold.co/... poster ✕
```

**After Running Script:**
```
Movie "Avatar" - TMDB real poster ✓
```

**Deleted:**
- "The Matrix" + 2 ratings + 1 watchlist
- "Inception" + 1 rating + 0 watchlist

---

## Safety Tips

1. **Backup first** (IMPORTANT!)
   ```bash
   cp instance/app.db instance/app.db.backup
   ```

2. **Run the cleanup**
   ```bash
   python remove_placeholder_movies.py
   ```

3. **Check results**
   - Look at remaining movies
   - Verify counts match expectations

4. **Keep backup for 30 days**
   - Just in case you need to restore

---

## Files

| File | Purpose |
|------|---------|
| `remove_placeholder_movies.py` | CLI script |
| `app/services/posters.py` | Core deletion function |
| `app/routes/admin.py` | Admin panel route |
| `app/templates/admin/remove_placeholder_movies.html` | Admin UI |

---

## Stats from Your Database

Run this to see placeholder counts:

```bash
.venv\Scripts\python.exe -c "
from app import create_app
from app.models import Movie

app = create_app()
with app.app_context():
    total = Movie.query.count()
    placeholders = Movie.query.filter(
        Movie.poster_url.like('%placehold.co%')
    ).count()
    real = total - placeholders
    
    print(f'Total movies: {total}')
    print(f'Real posters: {real}')
    print(f'Placeholder posters: {placeholders}')
    print(f'After cleanup: {real} movies')
"
```

---

## Result Example

```
Removing movies with placeholder posters...

Are you sure? (yes/no): yes

✓ Cleanup Complete!
  📽️  Movies removed: 506
  ⭐ Ratings deleted: 245
  📋 Watchlist items deleted: 89
```

---

**That's it! Quick, safe, and easy! 🎉**
