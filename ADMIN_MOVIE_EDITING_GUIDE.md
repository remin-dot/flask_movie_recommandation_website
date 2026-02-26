# 📽️ Admin Movie Editing Guide

## How to Edit Movies as Admin in the Web Interface

### Step-by-Step Guide

#### 1. **Access Admin Panel**
1. Login to your account (must be admin user)
2. Click **"Admin Panel"** in navigation menu
3. Go to **"Manage Movies"** or **"Dashboard"**

#### 2. **Find a Movie**

**Option A - Browse Movies:**
- Click **"Manage Movies"** from Admin Dashboard
- Scroll through the list
- Movies are sorted by newest first
- Shows: Title, Year, # of Ratings, Avg Rating, Poster type

**Option B - Search Movies:**
- Click **"Manage Movies"**
- Enter movie title in search box
- Click **"🔍 Search"** button
- Search works on title and description

#### 3. **View Movie Details**
1. In the movies list, click **"View"** button
2. See full movie information:
   - Title
   - Release year
   - TMDB ID
   - Poster URL (real or placeholder)
   - Genres
   - Full description
   - Ratings statistics
   - User reviews

#### 4. **Edit a Movie**

**From Movie List:**
1. Click **"Edit"** button in the movie row

**From Movie Detail Page:**
1. Click **"✎ Edit Movie"** button

**Edit Form Fields:**

| Field | Description |
|-------|-------------|
| **Movie Title** | The official movie name (e.g., "The Dark Knight") |
| **Release Year** | Year movie was released (1800-2099) |
| **TMDB ID** | The Movie Database ID (from themoviedb.org) |
| **Poster URL** | Direct link to poster image (https://...) |
| **Description** | Full movie plot/synopsis |
| **Genres** | Select all applicable genres (checkbox list) |

#### 5. **Make Changes**

**Example - Updating a Movie:**

```
Before:
- Title: "The Dark Knight Rises" (wrong)
- Year: 2012 ✓
- Description: Generic text
- Genres: Action (missing Drama, Crime)

After:
- Title: "The Dark Knight Rises" (corrected)
- Year: 2012 ✓
- Description: When the menace known as the Joker...
- Genres: Action, Crime, Drama, Thriller ✓
```

#### 6. **Save Changes**

1. Click **"💾 Save Changes"** button
2. System validates data
3. Shows success message
4. Returns to movie view page

#### 7. **Verify Changes**

1. Movie details updated
2. Changes appear immediately on public movie page
3. See "✓ Movie updated successfully" message

---

## Common Editing Tasks

### Update Title
```
Old: "Inception"
New: "Inception" ✓

Best Practice:
- Use full official title
- Include subtitles if any
- Match TMDB official title
```

### Fix Release Year
```
Old: Year 2010
New: Year 2010 ✓

Example:
- Movie says "2015" but actually "2014"
- Update to correct year
```

### Add Description
```
If blank or placeholder text, add:
- Official plot summary from TMDB
- 1-3 paragraphs
- Clear, concise description
```

### Link TMDB ID
```
1. Search movie on https://www.themoviedb.org
2. Find URL: themoviedb.org/movie/27205
3. Enter "27205" in TMDB ID field
4. This links to authoritative TMDB data
```

### Update Poster
```
1. Find real poster URL on TMDB
2. Right-click poster → Copy image link
3. Paste into "Poster URL" field
4. Replaces placeholder automatically
```

### Assign Genres
```
Before:
- No genres assigned

After:
- Action ✓
- Crime ✓
- Drama ✓
- Thriller ✓

Method:
1. Check relevant genre boxes
2. Uncheck if not applicable
3. Save changes
```

---

## Example: Complete Movie Edit

**Movie: "The Dark Knight"**

### Edit Form:
```
Movie Title:
  The Dark Knight

Release Year:
  2008

TMDB ID:
  155

Poster URL:
  https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg

Description:
  When the menace known as the Joker wreaks havoc on Gotham,
  Batman must accept one of the greatest psychological and 
  physical tests to fight injustice...
  
Genres:
  ☑ Action
  ☑ Crime
  ☑ Drama
  ☑ Thriller
  ☐ Comedy
  ☐ Family
```

**Click "💾 Save Changes"**

Result:
```
✓ Movie "The Dark Knight" updated successfully.
```

---

## Different Movie Views

### 📋 Manage Movies (List View)
- See all movies in table format
- Quick overview: Title, Year, Ratings, Poster Type
- Search and filter
- Jump to View or Edit with buttons
- Pagination for browsing

### 👁️ View Movie (Detail View)
- Full movie information
- Large poster thumbnail
- Statistics (ratings, avg rating, watchlist count)
- Associated user ratings and reviews
- Links to TMDB
- Edit or Delete buttons

### ✎ Edit Movie (Form View)
- All editable fields
- Genre selection
- Live poster preview (when editing)
- Help panel with tips
- Links to reference sources (TMDB, IMDb)
- Save or Cancel buttons

---

## Tips & Best Practices

### ✅ DO:
- Use official TMDB title
- Include subtitles (e.g., "Avatar: The Way of Water")
- Use complete, accurate descriptions
- Link TMDB ID for data integrity
- Assign all relevant genres
- Use high-quality poster images
- Check spelling and grammar

### ❌ DON'T:
- Use incomplete or abbreviated titles
- Use generic placeholder descriptions
- Leave TMDB ID blank (if available)
- Over-assign genres
- Use low-quality or broken image URLs
- Leave description field empty
- Skip genre assignments

---

## Troubleshooting

### Problem: Can't find Edit button
**Solution:**
- Click "View" on movie first
- Then click "✎ Edit Movie" on detail page

### Problem: Changes not saving
**Solution:**
1. Check all required fields filled (Title, Description)
2. Look for error message at top
3. Verify URL format (for poster)
4. Try again

### Problem: Poster image not showing
**Solution:**
1. Check URL is correct and complete
2. Start with: `https://`
3. Try copying from TMDB: themoviedb.org/movie/ID
4. Test URL in browser first

### Problem: Genre not available
**Solution:**
1. Go to **Admin → Manage Genres**
2. Create new genre if needed
3. Return to edit movie
4. Refresh page to see new genre

---

## Access Levels

| User Type | Can View | Can Edit | Can Delete |
|-----------|----------|----------|-----------|
| Regular User | ✓ | ✗ | ✗ |
| Admin | ✓ | ✓ | ✓ |

**Note:** Only administrators can edit movies via the web interface.

---

## Movie Structure

```
Movie Database Record
├── ID: Unique identifier
├── Title: Official movie name
├── Year: Release year
├── Description: Plot summary
├── Poster URL: Image link
├── TMDB ID: External database link
└── Genres: Multiple categories
```

---

## Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| Go to Manage Movies | `/admin/movies` |
| View Movie | `/admin/movies/[ID]` |
| Edit Movie | `/admin/movies/[ID]/edit` |
| Search Movies | Ctrl+F (on Manage page) |

---

## Real-World Workflow

### Daily Admin Work:
```
1. Go to Manage Movies
2. Filter recent additions
3. Check poster status
4. Click "Edit" on movies needing improvement
5. Add missing descriptions
6. Link TMDB IDs
7. Assign genres
8. Save changes
9. Verify on public site
```

### Weekly Maintenance:
```
1. Search for movies without descriptions
2. Update with accurate information
3. Fix incorrect years
4. Improve poster images
5. Ensure genre consistency
```

---

## Need Help?

1. **Finding TMDB ID:** Visit themoviedb.org, search movie
2. **Poster URL:** Right-click TMDB poster → Copy image link
3. **Movie Description:** Copy from TMDB official overview
4. **Genre Help:** Check TMDB movie page for official genres

---

**Ready to edit?** 🚀

Visit: **Admin Panel → Manage Movies → Click Edit**

Good luck organizing your movie database! ✨
