"""
Input validation utilities for the Flask application
"""

import re
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_username(username):
    """
    Validate username format
    - 3-20 characters
    - Letters, numbers, underscores only
    """
    if not username or len(username) < 3 or len(username) > 20:
        raise ValidationError("Username must be between 3 and 20 characters")
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValidationError("Username can only contain letters, numbers, and underscores")
    
    return True


def validate_email(email):
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not email or len(email) > 120:
        raise ValidationError("Invalid email address")
    
    if not re.match(pattern, email):
        raise ValidationError("Invalid email format")
    
    return True


def validate_password(password):
    """
    Validate password strength
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    """
    if not password or len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValidationError("Password must contain at least one digit")
    
    return True


def validate_rating(rating):
    """
    Validate movie rating
    - Must be between 1 and 5
    """
    try:
        rating_num = float(rating)
        if rating_num < 1 or rating_num > 5:
            raise ValidationError("Rating must be between 1 and 5")
        return True
    except (ValueError, TypeError):
        raise ValidationError("Invalid rating format")


def validate_search_query(query):
    """
    Validate and sanitize search query
    - 1-100 characters
    - Remove dangerous characters
    """
    if not query or len(query) > 100:
        raise ValidationError("Search query must be between 1 and 100 characters")
    
    # Remove potentially dangerous characters but allow common search patterns
    sanitized = re.sub(r'[<>\"\'%;()&+]', '', query).strip()
    
    if not sanitized:
        raise ValidationError("Search query contains invalid characters")
    
    return sanitized


def validate_movie_title(title):
    """
    Validate movie title
    - 1-255 characters
    """
    if not title or len(title) > 255:
        raise ValidationError("Movie title must be between 1 and 255 characters")
    
    return True.strip()


def validate_movie_year(year):
    """
    Validate movie year
    - Between 1800 and current year
    """
    try:
        year_num = int(year)
        current_year = datetime.now().year
        
        if year_num < 1800 or year_num > current_year + 5:
            raise ValidationError(f"Year must be between 1800 and {current_year + 5}")
        
        return True
    except (ValueError, TypeError):
        raise ValidationError("Invalid year format")
