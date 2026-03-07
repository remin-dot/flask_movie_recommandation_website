# Development Guide - MovieFlix

## Project Setup

### Prerequisites
- Python 3.8 or higher
- Git for version control
- A text editor or IDE (VS Code, PyCharm, etc.)

### Initial Setup

1. **Clone the repository**:
```bash
git clone https://github.com/remin-dot/test.git
cd test
```

2. **Create virtual environment**:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run the application**:
```bash
python run.py
# or
flask run
```

Visit `http://localhost:5000` in your browser.

---

## Project Architecture

### Directory Structure
```
test/
├── app/                          # Flask application package
│   ├── __init__.py              # App factory and initialization
│   ├── models.py                # Database models
│   ├── i18n.py                  # Internationalization
│   ├── routes/                  # API routes/blueprints
│   │   ├── auth.py             # Authentication routes
│   │   ├── movie.py            # Movie management routes
│   │   ├── admin.py            # Admin routes
│   │   └── user.py             # User profile routes
│   ├── services/                # Business logic
│   │   ├── recommendations.py  # Recommendation algorithms
│   │   ├── search_index.py     # Search functionality
│   │   ├── posters.py          # Movie poster processing
│   │   └── tmdb.py             # TMDB API integration
│   ├── templates/              # HTML templates
│   │   ├── base.html           # Base template
│   │   ├── auth/               # Auth templates
│   │   ├── movies/             # Movie templates
│   │   ├── admin/              # Admin templates
│   │   └── user/               # User templates
│   ├── static/                 # CSS, JS, images
│   │   ├── css/               # Stylesheets
│   │   └── js/                # JavaScript files
│   └── utils/                  # Utility functions
├── run.py                       # Application entry point
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
└── README.md                    # Main documentation

```

---

## Key Components

### 1. Models (app/models.py)

**User Model**
- Handles user accounts and authentication
- Password hashing with Werkzeug
- Relationships: ratings, watchlist entries

**Movie Model**
- Stores movie information
- Many-to-many relationship with genres
- Methods for rating calculation
- Relationships: ratings, watchlist entries

**Rating Model**
- User ratings for movies
- Stores rating value (1-5)
- Optional review text
- Timestamps for creation/update

**Watchlist Model**
- Tracks movies users want to watch
- Unique constraint: one entry per user-movie pair
- Timestamp for when added

**Genre Model**
- Movie categories
- Many-to-many relationship with movies

---

### 2. Routes (app/routes/)

**auth.py**: Authentication
- User registration and login
- Password validation
- Session management

**movie.py**: Movie Management
- Browse movies with pagination
- Movie detail pages
- Rating and watchlist operations
- Search functionality
- Recommendation engine

**admin.py**: Admin Functions
- User management
- Movie CRUD operations
- Genre management
- Statistics dashboard

**user.py**: User Profiles
- Dashboard with statistics
- Profile page with rating history
- Settings management

---

### 3. Services (app/services/)

**recommendations.py**
- Genre-based recommendations
- Collaborative filtering
- Popular movies algorithm
- Hybrid approach

**search_index.py**
- Full-text search capabilities
- Genre filtering
- Movie discovery features

**posters.py**
- Movie poster processing
- Image caching
- Poster synchronization

---

## Development Workflow

### Adding a New Feature

1. **Create or update models** (if needed)
```python
# In app/models.py
class NewModel(db.Model):
    __tablename__ = 'new_model'
    id = db.Column(db.Integer, primary_key=True)
    # ... add columns
```

2. **Create routes** (in appropriate blueprint)
```python
# In app/routes/module.py
@module_bp.route('/path')
def new_route():
    return render_template('template.html')
```

3. **Create templates** (in app/templates/)
```html
<!-- In app/templates/new_template.html -->
{% extends "base.html" %}
{% block content %}
  <h1>New Feature</h1>
{% endblock %}
```

4. **Add styling** (in app/static/css/)
```css
/* In app/static/css/style.css */
.new-feature {
    /* CSS rules */
}
```

5. **Test the feature**
```bash
python -m pytest tests/test_routes.py
```

6. **Commit changes**
```bash
git add .
git commit -m "feat: add new feature description"
```

---

## Database Management

### Creating Tables
Tables are automatically created on first run via `db.create_all()` in app/__init__.py

### Adding a Migration
For larger changes, use Flask-Migrate:
```bash
pip install Flask-Migrate
flask db init
flask db migrate -m "description"
flask db upgrade
```

### Seeding Sample Data
```python
from app import create_app, db
from app.models import Movie, Genre

app = create_app()
with app.app_context():
    action = Genre(name='Action')
    movie = Movie(title='My Movie', year=2023)
    movie.genres.append(action)
    db.session.add(movie)
    db.session.commit()
```

---

## Testing

### Run Tests
```bash
pytest                           # Run all tests
pytest tests/test_routes.py     # Run specific test file
pytest -v                       # Verbose output
pytest --cov                    # Coverage report
```

### Write a Test
```python
def test_movie_list(client):
    response = client.get('/movies')
    assert response.status_code == 200
    assert b'Movies' in response.data
```

---

## Code Style Guidelines

### Python
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Comment complex logic

### HTML/Templates
- Use semantic HTML
- Maintain consistent indentation
- Use Bootstrap classes
- Include i18n translations

### CSS
- Use CSS variables for colors
- Keep selectors specific
- Comment sections
- Use mobile-first approach

### JavaScript
- Use camelCase for variables
- Keep functions focused
- Add error handling
- Use `const` by default

---

## Common Commands

```bash
# Start development server
python run.py

# Run tests
pytest

# Create admin user
python run.py create-admin

# Seed sample data
python seed_movies.py

# Format code
black app/

# Check type hints
mypy app/

# Lint code
pylint app/

# Update requirements
pip freeze > requirements.txt
```

---

## Debugging

### Flask Debug Mode
```python
# In run.py
app.run(debug=True)  # Auto-reload, error page
```

### Debug Toolbar
```bash
pip install flask-debugtoolbar
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)
logger.debug('Debug message')
logger.error('Error message')
```

### Database Debugging
```python
# View raw SQL
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

@event.listens_for(SQLAlchemy().engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    print(statement)
```

---

## Deployment

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

### Deployment with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

---

## Contributing

### Git Workflow
1. Create feature branch: `git checkout -b feature/description`
2. Make changes and test thoroughly
3. Commit with clear messages: `git commit -m "type: description"`
4. Push to repository: `git push origin feature/description`
5. Submit pull request for review

### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code formatting
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `test`: Test additions
- `chore`: Build, dependencies

### Example Commit
```bash
git commit -m "feat: add watchlist CSRF token support

- Add CSRF token to fetch requests
- Update JavaScript watchlist functions
- Include token in request headers
- Fixes #123"
```

---

## Performance Tips

1. Use database indexing for frequently queried columns
2. Implement pagination for large datasets
3. Cache recommendations (recompute hourly)
4. Use lazy loading for relationships
5. Minify CSS/JavaScript for production
6. Use CDN for static files
7. Implement database connection pooling
8. Monitor query performance

---

## Security Best Practices

1. Keep dependencies updated
2. Use HTTPS in production
3. Implement rate limiting
4. Validate all user inputs
5. Use parameterized queries (SQLAlchemy does this)
6. Implement CSRF protection (flask-wtf)
7. Hash passwords (werkzeug)
8. Keep secrets in environment variables
9. Regular security audits
10. Keep logs for audit trails

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Python PEP 8](https://pep8.org/)
