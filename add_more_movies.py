"""
Add remaining movies to reach 1000 total
"""

from app import create_app, db
from app.models import Movie, Genre

app = create_app('development')

def add_more_movies():
    """Add additional movies to reach 1000"""
    with app.app_context():
        genres_list = [
            'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 
            'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror',
            'Musical', 'Mystery', 'Romance', 'Science Fiction', 'Thriller', 'War', 
            'Western', 'Sport', 'School'
        ]
        
        current_count = Movie.query.count()
        print(f"Current movies in database: {current_count}")
        
        needed = 1000 - current_count
        print(f"Movies needed to reach 1000: {needed}")
        
        # Get all existing titles
        existing_titles = {m.title for m in Movie.query.all()}
        
        # Comprehensive word lists for generating unique movie titles
        movie_parts = {
            'prefix': [
                'The Adventures of', 'The Mystery of', 'The Secret of', 'The Last',
                'Return to', 'Journey to', 'Battle of', 'Quest for', 'Search for',
                'Rise of', 'Fall of', 'Legend of', 'Tale of', 'Story of',
                'Chronicles of', 'Saga of', 'World of', 'Kingdom of', 'Empire of',
                'Beyond', 'Beyond the', 'Across the', 'Through the', 'Into the',
                'City of', 'Land of', 'Sea of', 'Sky of', 'Age of',
                'Time of', 'Day of', 'Night of', 'Hour of', 'Moment of',
                'Operation', 'Project', 'Mission', 'Code', 'File',
                'Secret', 'Lost', 'Forgotten', 'Ancient', 'Eternal',
                'Final', 'Last', 'First', 'New', 'Old',
                'Dark', 'Light', 'Bright', 'Shadow', 'Echo'
            ],
            'subject': [
                'Agent', 'Assassin', 'Spy', 'Detective', 'Investigator',
                'Knight', 'Warrior', 'Soldier', 'Hero', 'Villain',
                'King', 'Queen', 'Prince', 'Princess', 'Emperor',
                'Vampire', 'Werewolf', 'Demon', 'Angel', 'Ghost',
                'Robot', 'Android', 'Cyborg', 'AI', 'Machine',
                'Dragon', 'Phoenix', 'Eagle', 'Wolf', 'Tiger',
                'Master', 'Student', 'Teacher', 'Guardian', 'Mentor',
                'Nomad', 'Outlaw', 'Rebel', 'Rogue', 'Lone',
                'Twin', 'Shadow', 'Clone', 'Mirror', 'Echo',
                'Hunter', 'Predator', 'Prey', 'Survivor', 'Escape',
                'Formula', 'Cure', 'Virus', 'Plague', 'Zone',
                'Portal', 'Gateway', 'Bridge', 'Door', 'Window',
                'Planet', 'Star', 'Galaxy', 'Universe', 'Dimension',
                'Element', 'Force', 'Power', 'Energy', 'Source'
            ],
            'action': [
                'Rising', 'Falling', 'Breaking', 'Building', 'Destroying',
                'Seeking', 'Running', 'Fighting', 'Surviving', 'Escaping',
                'Awakening', 'Rising', 'Breaking', 'Shattering', 'Enduring',
                'Unleashed', 'Released', 'Exposed', 'Revealed', 'Discovered',
                'Ascending', 'Descending', 'Emerging', 'Vanishing', 'Returning',
                'Reborn', 'Resurrected', 'Transformed', 'Evolved', 'Changed'
            ],
            'suffix': [
                'Protocol', 'Mandate', 'Directive', 'Judgment', 'Verdict',
                'Reckoning', 'Awakening', 'Rising', 'Falling', 'Return',
                'Beginning', 'End', 'Middle', 'Prequel', 'Sequel',
                'Legacy', 'Heritage', 'Dynasty', 'Empire', 'Kingdom',
                'Revolution', 'Evolution', 'Resolution', 'Redemption', 'Revelation'
            ]
        }
        
        # Generate new unique movies
        movies_added = 0
        attempt = 0
        max_attempts = needed * 5  # Allow many attempts
        
        while movies_added < needed and attempt < max_attempts:
            attempt += 1
            
            # Randomly select parts to create title
            import random
            
            title_pattern = random.choice([
                '{prefix} {subject}',
                '{prefix} {subject} {action}',
                'The {subject} {action}',
                '{subject}: {action} {suffix}',
                '{prefix}: {subject} Returns',
                'Dark {subject}',
                'Silent {subject}',
                'The {subject} Protocol',
                '{subject} {action}',
                'Operation {subject}',
            ])
            
            try:
                title = title_pattern.format(
                    prefix=random.choice(movie_parts['prefix']),
                    subject=random.choice(movie_parts['subject']),
                    action=random.choice(movie_parts['action']),
                    suffix=random.choice(movie_parts['suffix'])
                )
            except:
                continue
            
            # Skip if title already exists
            if title in existing_titles:
                continue
            
            year = random.randint(1950, 2024)
            genre_count = random.randint(2, 3)
            selected_genres = random.sample(genres_list, genre_count)
            
            try:
                # Create movie
                movie = Movie(
                    title=title,
                    year=year,
                    description=f"A compelling {year} film titled '{title}'. Experience an unforgettable journey with outstanding performances and breathtaking cinematography.",
                    poster_url=f"https://via.placeholder.com/300x450?text={title.replace(' ', '+')[:30]}"
                )
                
                # Add genres
                for genre_name in selected_genres:
                    genre = Genre.query.filter_by(name=genre_name).first()
                    if genre:
                        movie.genres.append(genre)
                
                db.session.add(movie)
                existing_titles.add(title)
                movies_added += 1
                
                # Commit every 50 movies
                if movies_added % 50 == 0:
                    db.session.commit()
                    total = Movie.query.count()
                    print(f"  Progress: {total} movies | Added this batch: {movies_added}")
                    
            except Exception as e:
                db.session.rollback()
                print(f"Error adding movie '{title}': {str(e)}")
                continue
        
        # Final commit
        db.session.commit()
        total_movies = Movie.query.count()
        
        print(f"\n✓ Process complete!")
        print(f"✓ Total movies in database: {total_movies}")
        print(f"✓ Movies added in this run: {movies_added}")
        
        return total_movies

if __name__ == '__main__':
    print("Adding remaining movies to reach 1000...")
    print("=" * 60)
    add_more_movies()
    print("=" * 60)
    print("Done!")
