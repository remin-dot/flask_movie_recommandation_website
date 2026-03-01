# MovieFlix - Movie Recommendation Website

A full-stack web application for discovering, rating, and sharing movies with personalized recommendations based on user preferences.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3+-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**Repository**: https://github.com/remin-dot/flask_movie_recommandation_website.git

---

## 📖 Table of Contents

- [Features Overview](#-features-overview)
- [Technology Stack](#-technology-stack)
- [Installation & Setup](#-installation--setup)
- [Running the Application](#-running-the-application)
- [Project Architecture](#-project-architecture)
- [Database Models](#-database-models)
- [API Endpoints](#-api-endpoints)
- [Development Guide](#-development-guide)
- [Component Description](#-component-description)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)

---

## 🎬 Features Overview

### Core User Features
- **User Authentication**: Secure registration and login with password hashing
- **Movie Browse & Search**: Search movies by title, genre, and filters
- **Rating System**: Rate movies 1-5 stars with optional reviews
- **Watchlist**: Add/remove movies you want to watch
- **Personalized Recommendations**: Algorithm-based movie suggestions
- **User Dashboard**: Statistics, recent ratings, watchlist count
- **User Profile**: Viewing history, rating statistics, genre preferences
- **Genre Filtering**: Browse movies by category

### Technical Features
- **MVC Architecture**: Clean separation of concerns
- **SQLite Database**: Lightweight but powerful
- **Flask-Login**: Secure session management
- **SQLAlchemy ORM**: Database relationships
- **Bootstrap 5**: Responsive design
- **CSRF Protection**: Security against attacks
- **Password Hashing**: Werkzeug security
- **Internationalization**: Multi-language support (5 languages)
- **Dark Mode**: User preference support
- **Admin Dashboard**: Manage users, movies, genres, ratings

### Advanced Features
- **Collaborative Filtering**: User-based recommendations
- **Genre-Based Recommendations**: Similar movie suggestions
- **Hybrid Algorithm**: Combined recommendation approach
- **Real-time Search**: Fast movie discovery
- **Movie Sync**: TMDB API integration
- **Rate Limiting Ready**: Security framework in place

---

## 🏗️ Technology Stack

### Backend
- **Flask 3.1.1** - Web framework
- **Python 3.8+** - Language
- **SQLAlchemy 2.0.38** - ORM
- **Flask-SQLAlchemy 3.0.5** - Database integration
- **Flask-Login 0.6.3** - User authentication
- **Flask-WTF 1.2.2** - Forms & CSRF protection

### Frontend
- **Bootstrap 5.3** - UI framework
- **Jinja2** - Template engine
- **HTML5/CSS3** - Markup & styling
- **JavaScript** - Client-side logic
- **Font Awesome 6.4** - Icons

### Database
- **SQLite** - Data storage

### Tools
- **Git** - Version control
- **Pytest** - Testing
- **Gunicorn** - Production server
- **Docker** - Containerization

---

## 💾 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/remin-dot/flask_movie_recommandation_website.git
cd flask_movie_recommandation_website
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment
```bash
# Copy example to .env
cp .env.example .env

# Edit .env with your settings (if needed)
```

### Step 5: Run Application
```bash
python run.py
```

The application will start on `http://127.0.0.1:5000/`

---

## 🚀 Running the Application

### Development Mode
```bash
# Default: run.py
python run.py

# Or using Flask CLI
flask run

# With specific port
flask run --port 5001
```

### Production Mode
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Using Docker
```bash
docker-compose up --build
# Access at http://localhost:5000
```

### Create Admin User
The app creates an admin user on first run:
- Username: `admin`
- Email: `admin@example.com`
- Password: `adminpass`

Change these in the database before production!

---

## 🏗️ Project Architecture

### Directory Structure
```
flask_movie_recommandation_website/
├── app/                             # Main Flask package
│   ├── __init__.py                 # App factory & initialization
│   ├── models.py                   # Database models (User, Movie, Rating, etc.)
│   ├── i18n.py                     # Internationalization (5 languages)
│   ├── routes/
│   │   ├── auth.py                # Authentication routes
│   │   ├── movie.py               # Movie management routes
│   │   ├── admin.py               # Admin panel routes
│   │   ├── user.py                # User profile routes
│   │   └── __init__.py
│   ├── services/
│   │   ├── recommendations.py     # Recommendation algorithms
│   │   ├── search_index.py        # Full-text search
│   │   ├── posters.py             # Image processing
│   │   ├── tmdb.py                # TMDB API integration
│   │   └── __init__.py
│   ├── templates/
│   │   ├── base.html              # Base template
│   │   ├── home.html              # Homepage
│   │   ├── auth/                  # Login/Register
│   │   ├── movies/                # Movie pages
│   │   ├── user/                  # User pages
│   │   ├── admin/                 # Admin pages
│   │   └── errors/                # Error pages
│   ├── static/
│   │   ├── css/                   # Stylesheets
│   │   ├── js/                    # JavaScript files
│   │   ├── icons/                 # App icons
│   │   └── images/                # Images
│   └── utils/
│       ├── logger.py              # Logging utilities
│       ├── validation.py          # Form validation
│       └── __init__.py
│
├── tests/                          # Test suite
│   ├── conftest.py                # Test configuration
│   ├── test_auth.py               # Auth tests
│   ├── test_models.py             # Model tests
│   ├── test_routes.py             # Route tests
│   └── __init__.py
│
├── instance/                       # Instance-specific files
├── logs/                           # Application logs
│
├── run.py                          # Application entry point
├── config.py                       # Configuration
├── requirements.txt                # Dependencies
├── pytest.ini                      # Test config
├── Dockerfile                      # Docker image
├── docker-compose.yml              # Docker compose
├── .env                            # Environment variables
├── .env.example                    # Environment template
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

---

## 💾 Database Models

### User Model
```python
- id (Integer, Primary Key)
- username (String, Unique, Required)
- email (String, Unique, Required)
- password_hash (String, Required)
- is_admin (Boolean, default=False)
- created_at (DateTime)
- updated_at (DateTime)
- Relationships: ratings, watchlist, reviews
```

### Movie Model
```python
- id (Integer, Primary Key)
- title (String, Required)
- description (Text)
- year (Integer)
- poster_url (String)
- created_at (DateTime)
- updated_at (DateTime)
- Many-to-many: genres
- Relationships: ratings, watchlist
```

### Genre Model
```python
- id (Integer, Primary Key)
- name (String, Unique, Required)
- Many-to-many: movies
```

### Rating Model
```python
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key)
- movie_id (Integer, Foreign Key)
- rating (Integer, 1-5)
- review (Text, optional)
- created_at (DateTime)
- updated_at (DateTime)
- Unique constraint: (user_id, movie_id)
```

### Watchlist Model
```python
- id (Integer, Primary Key)
- user_id (Integer, Foreign Key)
- movie_id (Integer, Foreign Key)
- added_at (DateTime)
- Unique constraint: (user_id, movie_id)
```

---

## 🔌 API Endpoints

### Authentication Routes
```
POST   /auth/register              Register new user
POST   /auth/login                 Login user
GET    /auth/logout                Logout user
POST   /auth/change-password       Change password (login required)
```

### Movie Routes
```
GET    /movies                     List movies (paginated)
GET    /movie/<id>                Movie detail page
POST   /add-to-watchlist/<id>     Add to watchlist (AJAX)
POST   /remove-from-watchlist/<id>Remove from watchlist (AJAX)
GET    /search                     Search movies
```

### Rating Routes
```
GET    /rate-movie/<id>           Rating form
POST   /rate-movie/<id>           Submit rating
POST   /delete-rating/<id>        Delete rating (login required)
```

### User Routes
```
GET    /user/dashboard            User dashboard (login required)
GET    /user/profile              User profile (login required)
GET    /watchlist                 View watchlist (login required)
GET    /user/settings             User settings (login required)
```

### Recommendation Routes
```
GET    /recommendations           Get recommendations (login required)
```

### Admin Routes
```
GET    /admin/                    Admin dashboard (admin only)
GET    /admin/users               User management (admin only)
GET    /admin/movies              Movie management (admin only)
GET    /admin/ratings             Rating management (admin only)
GET    /admin/genres              Genre management (admin only)
```

### Response Format
All endpoints return:
- **HTML**: Standard page requests
- **JSON**: AJAX requests with `Content-Type: application/json`

---

## 🔧 Component Description

### Authentication System (auth.py)
Handles user registration, login, and session management.
- Password hashing with Werkzeug
- Email validation
- Session-based authentication
- Login required decorators

### Movie Management (movie.py)
Core functionality for browsing, rating, and watchlist operations.
- Pagination (12 items per page)
- Genre filtering
- Search functionality
- Rating calculations
- Recommendation algorithm

### User Services (user.py)
User dashboard and profile features.
- Dashboard with statistics
- Rating history
- Watchlist management
- User settings

### Admin Panel (admin.py)
Administrative features for content and user management.
- User management interface
- Movie CRUD operations
- Genre management
- Statistics dashboard
- Rating moderation

### Recommendation Service (services/recommendations.py)
Implements multiple recommendation algorithms:
- **Genre-based**: Similar movies in liked genres
- **Collaborative**: Based on user rating patterns
- **Popular**: Trending movies
- **Hybrid**: Combined approach

### Search Service (services/search_index.py)
Fast full-text search implementation.
- Title search
- Genre filtering
- Efficient indexing

---

## 🛠️ Development Guide

### Setting Up Development Environment
```bash
# Install dev dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
pytest

# Check coverage
pytest --cov=app
```

### Adding a New Feature

1. **Update Models** (if needed)
   ```python
   # In app/models.py
   class NewModel(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       # Add columns...
   ```

2. **Create Routes**
   ```python
   # In app/routes/module.py
   @module_bp.route('/path')
   def new_route():
       return render_template('template.html')
   ```

3. **Create Templates**
   ```html
   <!-- In app/templates/new_template.html -->
   {% extends "base.html" %}
   {% block content %}
       <h1>New Feature</h1>
   {% endblock %}
   ```

4. **Add Styling**
   ```css
   /* In app/static/css/style.css */
   .new-feature { /* styles */ }
   ```

5. **Test**
   ```bash
   pytest tests/test_routes.py
   ```

6. **Commit**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

### Code Style Guidelines
- Follow PEP 8 for Python
- Use meaningful variable names
- Add docstrings to functions/classes
- Comment complex logic
- Keep functions focused and small

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/description

# Make changes and test
make test

# Commit with clear messages
git commit -m "feat: description"

# Push to repository
git push origin feature/description

# Create pull request on GitHub
```

### Commit Message Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `perf`: Performance
- `test`: Tests
- `chore`: Build/dependencies

---

## 🐛 Troubleshooting

### Issue: Port Already in Use
**Solution**: Change port in run.py
```python
app.run(debug=True, port=5001)
```

### Issue: Database Errors
**Solution**: Delete database and restart
```bash
rm instance/*.db
python run.py
```

### Issue: Missing Dependencies
**Solution**: Reinstall requirements
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: Session/Login Problems
**Solution**: Use incognito mode or clear cookies

### Issue: Template Not Found
**Solution**: Check template path and refresh browser cache
```bash
Ctrl+Shift+R (Hard refresh)
```

### Issue: CSRF Token Error
**Solution**: Ensure form includes CSRF token
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

### Issue: Module Import Errors
**Solution**: Activate virtual environment
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

---

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG = False`
- [ ] Change `SECRET_KEY` to random value
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure environment variables
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS if needed
- [ ] Set up logging to file
- [ ] Configure database backups
- [ ] Set up monitoring/alerting
- [ ] Test error pages

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Using Docker
```bash
# Build image
docker build -t movieflix .

# Run container
docker run -p 5000:5000 movieflix

# Or use compose
docker-compose up
```

### Environment Variables
Create `.env` file with:
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://...
```

---

## 📊 Project Statistics

- **Total Commits**: 55+
- **Code Lines**: ~5,000+
- **HTML Templates**: 29
- **API Endpoints**: 50+
- **Database Models**: 6
- **Languages**: 5 (EN, TH, JA, ZH, ES)

---

## 📚 Learning Outcomes

This project demonstrates:
- Flask web development fundamentals
- SQLAlchemy ORM usage
- User authentication & authorization
- Database design & relationships
- Jinja2 template inheritance
- Bootstrap responsive design
- RESTful API concepts
- Form handling & validation
- Error handling & logging
- Git version control
- Test-driven development

---

## 📄 License

MIT License - Feel free to use, modify, and distribute

---

## 🤝 Contributing

Contributions welcome! Please:
1. Report bugs via issues
2. Suggest improvements
3. Submit pull requests
4. Improve documentation

---

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review code comments
3. Check Flask documentation
4. Open a GitHub issue

---

## 🔄 Future Enhancements

Planned improvements:
- [ ] Email verification
- [ ] Advanced filtering
- [ ] User following system
- [ ] Movie collections
- [ ] Social features
- [ ] API tokens
- [ ] Rate limiting
- [ ] Performance monitoring
- [ ] Advanced analytics
- [ ] Machine learning recommendations

---

**Made with ❤️ for Movie Lovers**
