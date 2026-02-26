# MovieFlix - Movie Recommendation Website

A full-stack web application for discovering, rating, and sharing movies with personalized recommendations based on user preferences.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3+-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎬 Features

### Core Features
- **User Authentication**: Secure registration and login system with password hashing
- **Movie Management**: Browse, search, and add movies to the database
- **Rating System**: Rate movies from 1 to 5 stars with written reviews
- **Watchlist**: Keep track of movies you want to watch
- **Personalized Recommendations**: Get movie suggestions based on your ratings
- **User Dashboard**: View your rating history and statistics
- **User Profile**: Track all your ratings and viewing statistics
- **Search Functionality**: Search movies by title or genre
- **Genre Filtering**: Browse movies by specific genres

### Technical Features
- **MVC Architecture**: Clean separation of concerns
- **SQLite Database**: Lightweight but powerful data storage
- **Flask-Login**: Secure user session management
- **SQLAlchemy ORM**: Efficient database operations
- **Bootstrap 5**: Responsive and modern UI design
- **Jinja2 Templates**: Dynamic template rendering
- **Password Security**: Werkzeug password hashing

## 📋 Project Structure

```
flask_website/
├── run.py                          # Primary application entry point
├── app/                            # Main package (factory, routes, templates, static)
├── app.py                          # Legacy single-file app (kept for compatibility)
├── models.py                       # Legacy database models
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── movie_recommendation.db         # SQLite database (auto-created)
│
├── templates/                      # HTML templates
│   ├── base.html                  # Base template with navigation
│   ├── home.html                  # Home page with featured movies
│   ├── register.html              # User registration page
│   ├── login.html                 # User login page
│   ├── dashboard.html             # User dashboard
│   ├── movie_list.html            # All movies with pagination
│   ├── movie_detail.html          # Movie details with reviews
│   ├── add_movie.html             # Add new movie form
│   ├── rate_movie.html            # Rate and review movie
│   ├── recommendations.html       # Personalized recommendations
│   ├── watchlist.html             # User's watchlist
│   ├── profile.html               # User profile and statistics
│   ├── search_results.html        # Search results page
│   ├── 404.html                   # 404 error page
│   └── 500.html                   # 500 error page
│
└── static/                         # Static files
    ├── css/
    │   └── style.css              # Custom CSS styles
    └── js/
        └── script.js              # JavaScript functionality
```

## 🗄️ Database Models

### User Model
```python
- id (Integer, Primary Key)
- username (String, Unique)
- email (String, Unique)
- password_hash (String)
- created_at (DateTime)
- relationships: ratings, watchlist
```

### Movie Model
```python
- id (Integer, Primary Key)
- title (String)
- genre (String)
- description (Text)
- year (Integer)
- created_at (DateTime)
- relationships: ratings, watchlist
```

### Rating Model
```python
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key)
- movie_id (Integer, Foreign Key)
- rating (Integer, 1-5)
- review (Text, Optional)
- created_at (DateTime)
- updated_at (DateTime)
- unique constraint: (user_id, movie_id)
```

### Watchlist Model
```python
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key)
- movie_id (Integer, Foreign Key)
- added_at (DateTime)
- unique constraint: (user_id, movie_id)
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Clone or Download the Project
```bash
cd flask_website
```

### Step 2: Create a Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python run.py
```

The application will start on `http://127.0.0.1:5000/`

## 🌐 Routes Overview

### Authentication Routes
- `GET /register` - Registration page
- `POST /register` - Handle registration
- `GET /login` - Login page
- `POST /login` - Handle login
- `GET /logout` - Logout user

### Main Pages
- `GET /` - Home page
- `GET /dashboard` - User dashboard (requires login)
- `GET /profile` - User profile (requires login)

### Movie Management
- `GET /movies` - List all movies with pagination
- `GET /movie/<id>` - Movie detail page
- `GET /add-movie` - Add movie form (requires login)
- `POST /add-movie` - Submit new movie

### Ratings & Reviews
- `GET /rate-movie/<id>` - Rate movie form (requires login)
- `POST /rate-movie/<id>` - Submit rating
- `POST /delete-rating/<id>` - Delete user's rating

### Watchlist
- `GET /watchlist` - View watchlist (requires login)
- `POST /add-to-watchlist/<id>` - Add to watchlist (JSON)
- `POST /remove-from-watchlist/<id>` - Remove from watchlist (JSON)

### Recommendations & Search
- `GET /recommendations` - Personalized recommendations (requires login)
- `GET /search` - Search movies by title or genre

## 📝 Usage Guide

### 1. Create an Account
- Click "Register" in the navigation bar
- Fill in username, email, and password
- Submit the form

### 2. Browse Movies
- Navigate to "Movies" to see all movies
- Use genre filters to narrow down
- Use the search bar to find specific movies

### 3. Rate a Movie
- Click on a movie to view details
- Click "Rate This Movie"
- Select rating and optionally write a review
- Click "Save Rating"

### 4. Add to Watchlist
- On the movie detail page, click "Add to Watchlist"
- View your watchlist anytime from the navigation menu

### 5. Get Recommendations
- Rate at least one movie with 4-5 stars
- Go to "Recommendations" to see personalized suggestions
- Movies are recommended based on genres you like

### 6. Add New Movies
- Click "Add Movie" in the navigation
- Fill in movie details (title, genre, year, description)
- Submit the form

### 7. View Your Profile
- Click your username in the navigation
- Select "Profile" to see your stats and rating history
- View rating distribution chart and recent ratings

## ⚙️ Configuration

### Edit Secret Key (Important for Production)
In `app.py`, line 12:
```python
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
```

Change to a secure random key for production use.

### Database Location
By default, the SQLite database is created in the project root:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_recommendation.db'
```

### Debug Mode
To disable debug mode in production:
```python
app.run(debug=False)
```

## 🎯 How Recommendations Work

1. **Identify Highly Rated Movies**: The system finds all movies you rated 4-5 stars
2. **Extract Genres**: Collects genres from your highly-rated movies
3. **Find Unrated Movies**: Searches for movies in those genres you haven't rated yet
4. **Display Results**: Shows up to 12 recommended movies

Example: If you rate "Inception" and "Dune" (both Sci-Fi) with 5 stars, you'll get recommendations for other Sci-Fi movies.

## 🔐 Security Features

- **Password Hashing**: Uses Werkzeug's `generate_password_hash` and `check_password_hash`
- **Session Management**: Flask-Login handles secure user sessions
- **CSRF Protection**: Built-in Flask templates include CSRF tokens
- **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
- **Authentication Required**: Protected routes require login
- **Unique Constraints**: Database enforces one rating per movie per user

## 🎨 Customization

### Change Colors in CSS
Edit `static/css/style.css` and modify the CSS variables:
```css
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    /* Add more colors */
}
```

### Add More Genres
In `add_movie.html`, add new `<option>` tags:
```html
<option value="Your Genre">Your Genre</option>
```

### Modify Sample Data
In `app.py`, edit the `sample_movies` list in the `init_db()` function.

## 🐛 Troubleshooting

### Database Error
If you get database errors, delete `movie_recommendation.db` and restart the app. It will recreate automatically.

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, host='127.0.0.1', port=5001)
```

### Missing Dependencies
Reinstall requirements:
```bash
pip install -r requirements.txt --force-reinstall
```

### Session/Login Issues
Clear browser cookies or use incognito mode.

## 📊 Sample Data

The application comes with 10 pre-loaded movies:
- The Shawshank Redemption (Drama)
- The Dark Knight (Action)
- Inception (Sci-Fi)
- Dune (Sci-Fi)
- The Grand Budapest Hotel (Comedy)
- Parasite (Drama)
- Avatar (Sci-Fi)
- Pulp Fiction (Crime)
- Forrest Gump (Drama)
- Interstellar (Sci-Fi)

## 🚀 Deployment

For production deployment, consider:

1. **Use a production WSGI server** (Gunicorn, Waitress)
2. **Set up a proper database** (PostgreSQL, MySQL)
3. **Use environment variables** for sensitive data
4. **Enable HTTPS** with SSL/TLS
5. **Set DEBUG = False**
6. **Use a reverse proxy** (Nginx, Apache)

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app
```

## 📚 Dependencies

- **Flask** (2.3.3) - Web framework
- **Flask-SQLAlchemy** (3.0.5) - Database ORM
- **Flask-Login** (0.6.2) - User authentication
- **Werkzeug** (2.3.7) - Security utilities

All dependencies are listed in `requirements.txt`.

## 🎓 Learning Outcomes

This project demonstrates:
- Flask web development fundamentals
- SQLAlchemy ORM usage
- User authentication and authorization
- Database design and relationships
- Template inheritance in Jinja2
- Bootstrap responsive design
- RESTful API concepts
- Form handling and validation
- Error handling and logging

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest improvements
- Submit pull requests
- Improve documentation

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Check Flask and SQLAlchemy documentation

## 🔄 Future Enhancements

Possible improvements:
- [ ] Email verification for registration
- [ ] Advanced filtering and sorting
- [ ] Movie image uploads
- [ ] Social sharing features
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] API endpoints
- [ ] Elasticsearch for better search
- [ ] Collaborative filtering recommendations
- [ ] User following system
- [ ] Movie reviews by critics
- [ ] Trailer/streaming links

## 👨‍💻 Developer Notes

### Adding a New Feature
1. Update models if needed
2. Add routes in `app.py`
3. Create templates
4. Add styling in CSS
5. Test thoroughly

### Code Style
- Use meaningful variable names
- Add comments for complex logic
- Follow PEP 8 conventions
- Keep functions focused and small

## 📖 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)

---

**Created**: 2024
**Version**: 1.0.0
**Status**: Production Ready

Enjoy MovieFlix! 🎬🍿
