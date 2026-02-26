"""
Application entry point
Run this file to start the Flask development server
"""

import os
import json
import random
import click
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, Movie, Rating, Watchlist, Genre
from app.services.posters import (
    get_poster_for_movie, 
    sync_movie_posters, 
    remove_duplicate_movies,
    fetch_missing_posters,
    update_all_movie_posters
)


# Load environment variables from .env file
load_dotenv()

# Create app with configuration from environment
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)


@app.shell_context_processor
def make_shell_context():
    """Register models for Flask shell"""
    return {
        'db': db,
        'User': User,
        'Movie': Movie,
        'Rating': Rating,
        'Watchlist': Watchlist,
        'Genre': Genre
    }


@app.cli.command()
def init_db():
    """Initialize database with sample data"""
    db.create_all()
    
    # Check if database already has genres
    if Genre.query.first() is not None:
        removed = remove_duplicate_movies()
        if removed:
            print(f"Removed duplicate movies: {removed}")
        sync_movie_posters()
        print("Database already initialized.")
        return
    
    print("Initializing database...")
    
    # Add sample genres
    genres_data = [
        'Action',
        'Adventure',
        'Animation',
        'Comedy',
        'Crime',
        'Documentary',
        'Drama',
        'Family',
        'Fantasy',
        'History',
        'Horror',
        'Music',
        'Mystery',
        'Romance',
        'Science Fiction',
        'Thriller',
        'War',
        'Western',
    ]
    
    for genre_name in genres_data:
        if not Genre.query.filter_by(name=genre_name).first():
            genre = Genre(name=genre_name)
            db.session.add(genre)
    
    db.session.commit()
    
    # Add sample movies
    sample_movies = [
        {
            'title': 'The Shawshank Redemption',
            'genres': ['Drama'],
            'year': 1994,
            'description': 'Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.',
            'poster_url': get_poster_for_movie('The Shawshank Redemption', 1994)
        },
        {
            'title': 'The Dark Knight',
            'genres': ['Action', 'Crime', 'Drama'],
            'year': 2008,
            'description': 'When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest tests.',
            'poster_url': get_poster_for_movie('The Dark Knight', 2008)
        },
        {
            'title': 'Inception',
            'genres': ['Action', 'Science Fiction', 'Thriller'],
            'year': 2010,
            'description': 'A skilled thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea.',
            'poster_url': get_poster_for_movie('Inception', 2010)
        },
        {
            'title': 'Dune',
            'genres': ['Action', 'Adventure', 'Fantasy', 'Science Fiction'],
            'year': 2021,
            'description': 'Paul Atreides, a brilliant young man, must travel to the dangerous planet Arrakis to ensure the future of his family and people.',
            'poster_url': get_poster_for_movie('Dune', 2021)
        },
        {
            'title': 'The Grand Budapest Hotel',
            'genres': ['Adventure', 'Comedy', 'Crime'],
            'year': 2014,
            'description': 'A writer encounters the owner of an aging high-class hotel, who tells him of his early years serving as a lobby boy.',
            'poster_url': get_poster_for_movie('The Grand Budapest Hotel', 2014)
        },
        {
            'title': 'Parasite',
            'genres': ['Drama', 'Thriller'],
            'year': 2019,
            'description': 'Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.',
            'poster_url': get_poster_for_movie('Parasite', 2019)
        },
        {
            'title': 'Avatar',
            'genres': ['Action', 'Adventure', 'Fantasy', 'Science Fiction'],
            'year': 2009,
            'description': 'A paraplegic Marine dispatched to the moon Pandora must lead a Native American-like alien race in a revolt against invading forces.',
            'poster_url': get_poster_for_movie('Avatar', 2009)
        },
        {
            'title': 'Pulp Fiction',
            'genres': ['Crime', 'Drama'],
            'year': 1994,
            'description': 'The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.',
            'poster_url': get_poster_for_movie('Pulp Fiction', 1994)
        },
        {
            'title': 'Forrest Gump',
            'genres': ['Drama', 'Romance'],
            'year': 1994,
            'description': 'The presidencies of Kennedy and Johnson unfold as a man, while attending a film in 1994, recounts his life before the movie begins.',
            'poster_url': get_poster_for_movie('Forrest Gump', 1994)
        },
        {
            'title': 'Interstellar',
            'genres': ['Adventure', 'Drama', 'Science Fiction'],
            'year': 2014,
            'description': 'A team of explorers travel through a wormhole in space in an attempt to ensure humanity\'s survival.',
            'poster_url': get_poster_for_movie('Interstellar', 2014)
        },
    ]
    
    for movie_data in sample_movies:
        movie = Movie(
            title=movie_data['title'],
            description=movie_data['description'],
            year=movie_data['year'],
            poster_url=movie_data['poster_url']
        )
        
        for genre_name in movie_data['genres']:
            genre = Genre.query.filter_by(name=genre_name).first()
            if genre:
                movie.genres.append(genre)
        
        db.session.add(movie)
    
    db.session.commit()
    removed = remove_duplicate_movies()
    if removed:
        print(f"Removed duplicate movies: {removed}")
    sync_movie_posters()
    
    print("Database initialized successfully!")


@app.cli.command('seed_synthetic')
@click.option('--count', default=10000, type=int, help='Number of synthetic movies to add.')
@click.option('--clear', is_flag=True, help='Clear existing movies before seeding.')
def seed_synthetic(count, clear):
    """Seed the database with synthetic movies (no external APIs)."""
    if clear:
        Rating.query.delete()
        Watchlist.query.delete()
        Movie.query.delete()
        db.session.commit()

    genre_names = [
        'Action', 'Adventure', 'Animation', 'Comedy', 'Crime', 'Documentary', 'Drama',
        'Family', 'Fantasy', 'History', 'Horror', 'Music', 'Mystery', 'Romance',
        'Science Fiction', 'Thriller', 'War', 'Western',
    ]

    for name in genre_names:
        if not Genre.query.filter_by(name=name).first():
            db.session.add(Genre(name=name))
    db.session.commit()

    genres = Genre.query.order_by(Genre.id).all()

    title_adjectives = [
        'Crimson', 'Silent', 'Forgotten', 'Golden', 'Electric', 'Midnight', 'Hidden',
        'Stellar', 'Echoing', 'Velvet', 'Emerald', 'Shadow', 'Feral', 'Lunar',
        'Granite', 'Wild', 'Iridescent', 'Ivory', 'Autumn', 'Neon',
    ]
    title_nouns = [
        'Voyage', 'Signal', 'Archive', 'Frontier', 'Harbor', 'Circuit', 'Oracle',
        'Labyrinth', 'Compass', 'Summit', 'Horizon', 'Gambit', 'Pulse', 'Rift',
        'Sanctuary', 'Reckoning', 'Mirage', 'Awakening', 'Odyssey', 'Blueprint',
    ]
    plot_hooks = [
        'a reluctant hero', 'a rogue scientist', 'an unlikely duo', 'a haunted investigator',
        'a time-lost traveler', 'a fading star', 'a secret society', 'a stranded crew',
        'a master thief', 'a young prodigy',
    ]
    plot_hooks_th = [
        'วีรบุรุษที่ไม่เต็มใจ', 'นักวิทยาศาสตร์นอกคอก', 'คู่หูที่ไม่น่าเป็นไปได้',
        'นักสืบผู้ถูกหลอกหลอน', 'นักเดินทางหลุดเวลา', 'ดาวที่กำลังดับ',
        'สมาคมลับ', 'ลูกเรือที่ติดค้าง', 'โจรมือฉกาจ', 'อัจฉริยะรุ่นเยาว์',
    ]
    settings = [
        'in a coastal city', 'across a desert wasteland', 'on a remote moon',
        'inside a floating metropolis', 'beneath a frozen ocean', 'in a neon mega-city',
        'through forgotten ruins', 'on the edge of a war-torn kingdom',
        'inside a hidden valley', 'across a shifting dreamscape',
    ]
    settings_th = [
        'ในเมืองชายฝั่ง', 'ท่ามกลางทะเลทรายรกร้าง', 'บนดวงจันทร์ห่างไกล',
        'ภายในมหานครลอยฟ้า', 'ใต้มหาสมุทรน้ำแข็ง', 'ในมหานครนีออน',
        'ผ่านซากปรักหักพังที่ถูกลืม', 'ชายขอบอาณาจักรที่เต็มไปด้วยสงคราม',
        'ในหุบเขาลับ', 'ผ่านห้วงฝันที่เปลี่ยนแปลงตลอดเวลา',
    ]

    poster_url = '/static/images/poster-placeholder.svg'
    start_index = Movie.query.count()
    target = max(count, 0)
    batch_size = 500

    for i in range(start_index, start_index + target):
        adj = random.choice(title_adjectives)
        noun = random.choice(title_nouns)
        title = f"{adj} {noun} {i:05d}"
        year = random.randint(1980, 2025)
        hook = random.choice(plot_hooks)
        hook_th = random.choice(plot_hooks_th)
        setting = random.choice(settings)
        setting_th = random.choice(settings_th)

        description_en = (
            f"In {year}, {hook} finds a way to survive {setting}, "
            "uncovering a mystery that reshapes their future and everyone around them."
        )
        description_th = (
            f"ในปี {year} {hook_th} ต้องเอาตัวรอด {setting_th} "
            "และค้นพบความลับที่เปลี่ยนอนาคตของพวกเขาไปตลอดกาล"
        )

        description = json.dumps({'en': description_en, 'th': description_th}, ensure_ascii=False)

        movie = Movie(
            title=title,
            description=description,
            year=year,
            poster_url=poster_url,
        )

        if genres:
            movie.genres = random.sample(genres, k=random.randint(1, min(3, len(genres))))

        db.session.add(movie)

        if (i - start_index + 1) % batch_size == 0:
            db.session.commit()

    db.session.commit()
    print(f"Seeded {target} synthetic movies.")


@app.cli.command('sync_posters')
def sync_posters_command():
    """Remove duplicate movies and sync poster URLs."""
    removed = remove_duplicate_movies()
    result = sync_movie_posters()
    print(f"Removed duplicate movies: {removed}")
    print(f"Poster updates: {result.get('changed', 0)}")
    print(f"Duplicate poster fixes: {result.get('duplicate_fixes', 0)}")


@app.cli.command('fetch_posters')
def fetch_posters_command():
    """Fetch missing posters from TMDB API for all movies without posters."""
    print("Fetching missing posters from TMDB API...")
    
    if not app.config.get('TMDB_API_KEY'):
        print("⚠️  Warning: TMDB_API_KEY not configured in .env")
        print("Set TMDB_API_KEY to enable TMDB poster fetching")
        print("Get your key at: https://www.themoviedb.org/settings/api")
    
    result = fetch_missing_posters()
    print(f"✓ Total movies processed: {result['total']}")
    print(f"✓ Posters fetched from TMDB: {result['fetched']}")
    print(f"✓ Placeholder posters created: {result['failed']}")


@app.cli.command('update_posters')
@click.option('--force', is_flag=True, help='Force re-fetch all posters including existing ones')
def update_posters_command(force):
    """Update all movie posters from TMDB API."""
    if force:
        print("Force-updating all movie posters...")
    else:
        print("Updating missing movie posters...")
    
    if not app.config.get('TMDB_API_KEY'):
        print("⚠️  Warning: TMDB_API_KEY not configured in .env")
        print("Set TMDB_API_KEY to enable TMDB poster fetching")
        print("Get your key at: https://www.themoviedb.org/settings/api")
    
    result = update_all_movie_posters(force=force)
    print(f"✓ Total movies processed: {result['total']}")
    print(f"✓ Posters updated: {result['updated']}")
    print(f"✓ Posters unchanged: {result['kept']}")



@app.cli.command()
def create_admin():
    """Create an admin user"""
    from getpass import getpass
    
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = getpass("Enter admin password: ")
    
    if User.query.filter_by(username=username).first():
        print("Username already exists!")
        return
    
    if User.query.filter_by(email=email).first():
        print("Email already exists!")
        return
    
    admin = User(username=username, email=email, is_admin=True)
    admin.set_password(password)
    
    db.session.add(admin)
    db.session.commit()
    
    print(f"Admin user '{username}' created successfully!")


if __name__ == '__main__':
    app.run()
