# API Documentation - MovieFlix

## Authentication Endpoints

### POST /auth/register
**Description**: Register a new user account

**Request Body**:
```json
{
  "username": "string (3-20 chars, alphanumeric + underscore)",
  "email": "string (valid email)",
  "password": "string (min 6 chars)"
}
```

**Response**:
- 201 Created: User successfully registered
- 400 Bad Request: Validation error
- 409 Conflict: User already exists

---

### POST /auth/login
**Description**: Login with username and password

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
- 200 OK: Successfully logged in (sets session cookie)
- 401 Unauthorized: Invalid credentials
- 404 Not Found: User not found

---

### GET /auth/logout
**Description**: Logout current user

**Response**:
- 302 Redirect: Logout successful, redirects to home

---

## Movie Endpoints

### GET /movies
**Parameters**:
- `page` (optional): Page number (default: 1)
- `genre` (optional): Filter by genre
- `sort` (optional): Sort by 'recent', 'rating', 'oldest'

**Response**: HTML page with paginated movies

---

### GET /movie/<id>
**Description**: Get detailed information about a movie

**Response**: HTML page with movie details, ratings, and actions

---

### POST /add-to-watchlist/<movie_id>
**Description**: Add a movie to user's watchlist (requires login)

**Headers**:
- `X-CSRFToken`: CSRF token

**Response**:
```json
{
  "success": true,
  "message": "Added to watchlist"
}
```

---

### POST /remove-from-watchlist/<movie_id>
**Description**: Remove a movie from user's watchlist (requires login)

**Headers**:
- `X-CSRFToken`: CSRF token

**Response**:
```json
{
  "success": true,
  "message": "Removed from watchlist"
}
```

---

## Rating Endpoints

### GET /rate-movie/<movie_id>
**Description**: Display rating form for a movie (requires login)

**Response**: HTML form for rating a movie

---

### POST /rate-movie/<movie_id>
**Description**: Submit a rating for a movie (requires login)

**Request Body**:
```json
{
  "rating": 1-5,
  "review": "string (optional)"
}
```

**Response**:
- 201 Created: Rating created successfully
- 200 OK: Rating updated
- 400 Bad Request: Invalid data
- 404 Not Found: Movie not found

---

### POST /delete-rating/<movie_id>
**Description**: Delete user's rating for a movie (requires login)

**Response**:
- 200 OK: Rating deleted
- 404 Not Found: Rating not found

---

## User Endpoints

### GET /user/dashboard
**Description**: Get user dashboard with statistics (requires login)

**Response**: HTML page with dashboard data

---

### GET /user/profile
**Description**: Get user profile with rating history (requires login)

**Parameters**:
- `page` (optional): Page number for ratings pagination

**Response**: HTML page with user profile

---

### GET /watchlist
**Description**: Get user's watchlist (requires login)

**Parameters**:
- `page` (optional): Page number for watchlist pagination

**Response**: HTML page with watchlist items

---

## Recommendation Endpoints

### GET /recommendations
**Description**: Get personalized movie recommendations (requires login)

**Parameters**:
- `algorithm` (optional): 'genre', 'collaborative', 'popular', 'combined'

**Response**: HTML page with recommended movies

---

## Search Endpoints

### GET /search
**Description**: Search for movies by title or genre

**Parameters**:
- `q` (required): Search query
- `type` (optional): 'title', 'genre', 'all'

**Response**: HTML page with search results

---

## Admin Endpoints

### GET /admin/
**Description**: Admin dashboard (admin only)

**Response**: HTML page with admin statistics

---

### GET /admin/users
**Description**: List all users (admin only)

**Parameters**:
- `page` (optional): Page number

**Response**: HTML page with user list

---

### GET /admin/movies
**Description**: Manage movies (admin only)

**Parameters**:
- `page` (optional): Page number
- `search` (optional): Search movies

**Response**: HTML page with movie management

---

### POST /admin/movies
**Description**: Create a new movie (admin only)

**Request Body**:
```json
{
  "title": "string",
  "year": "integer",
  "description": "string",
  "genres": ["string"],
  "poster_url": "string (optional)"
}
```

**Response**:
- 201 Created: Movie created
- 400 Bad Request: Invalid data

---

### PUT /admin/movies/<id>
**Description**: Update a movie (admin only)

**Request Body**: Same as POST

**Response**:
- 200 OK: Movie updated
- 404 Not Found: Movie not found

---

### DELETE /admin/movies/<id>
**Description**: Delete a movie (admin only)

**Response**:
- 200 OK: Movie deleted
- 404 Not Found: Movie not found

---

## Error Responses

All endpoints may return:

### 400 Bad Request
```json
{
  "error": "Invalid request data",
  "details": "..."
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "..."
}
```

---

## Rate Limiting

Currently, rate limiting is not implemented. Future versions will include:
- 100 requests per minute per IP
- 1000 requests per hour per user

---

## Authentication

Most endpoints (except /auth/register, /auth/login, /movies, /search) require:
- User to be logged in (session cookie)
- CSRF token in POST requests (via X-CSRFToken header or form field)

---

## Response Formats

- **HTML**: Returns rendered HTML template
- **JSON**: Returns JSON response (for AJAX/API calls)

Specify preference via:
- Standard page requests return HTML
- AJAX requests with `Content-Type: application/json` return JSON
