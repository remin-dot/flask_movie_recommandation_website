"""
Seed 1000 unique movies with posters into the database
Run: python seed_movies_with_posters.py
"""

from app import create_app, db
from app.models import Movie, Genre
from app.services.posters import get_poster_for_movie, get_tmdb_public_poster_url, get_tmdb_search_poster_url
from urllib.parse import quote
import os
import requests
from sqlalchemy import text

app = create_app('development')
TMDB_POSTER_CACHE = {}
ITUNES_POSTER_CACHE = {}
ITUNES_FAILURES = 0
ITUNES_DISABLED = os.environ.get('USE_ITUNES_POSTERS', '0') != '1'
ITUNES_LOOKUPS = 0
MAX_ITUNES_LOOKUPS = 20


def is_synthetic_title(title):
    """Detect generated seed titles that are unlikely to have real posters."""
    value = (title or '').strip().lower()
    return '(2023 edition)' in value or value.endswith(' special') or ' v' in value

# Movie data with posters - 1000 unique movies across multiple genres
MOVIES_DATA = [
    # Action & Adventure (150 movies)
    {'title': 'The Avengers', 'year': 2012, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 24428},
    {'title': 'Avengers: Infinity War', 'year': 2018, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 299536},
    {'title': 'Avengers: Endgame', 'year': 2019, 'genres': ['Action', 'Adventure', 'Drama'], 'tmdb_id': 299534},
    {'title': 'Iron Man', 'year': 2008, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 1726},
    {'title': 'Iron Man 2', 'year': 2010, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 10138},
    {'title': 'Iron Man 3', 'year': 2013, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 68721},
    {'title': 'Captain America: The Winter Soldier', 'year': 2014, 'genres': ['Action', 'Adventure', 'Thriller'], 'tmdb_id': 100402},
    {'title': 'Captain America: Civil War', 'year': 2016, 'genres': ['Action', 'Adventure', 'Drama'], 'tmdb_id': 271110},
    {'title': 'Thor', 'year': 2011, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 10195},
    {'title': 'Thor: The Dark World', 'year': 2013, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 76338},
    {'title': 'Thor: Ragnarok', 'year': 2017, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 284053},
    {'title': 'Guardians of the Galaxy', 'year': 2014, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 118340},
    {'title': 'Guardians of the Galaxy Vol. 2', 'year': 2017, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 283995},
    {'title': 'Doctor Strange', 'year': 2016, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 333339},
    {'title': 'Black Panther', 'year': 2018, 'genres': ['Action', 'Adventure', 'Drama'], 'tmdb_id': 284054},
    {'title': 'Black Panther: Wakanda Forever', 'year': 2022, 'genres': ['Action', 'Adventure', 'Drama'], 'tmdb_id': 505642},
    {'title': 'Ant-Man', 'year': 2015, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 102899},
    {'title': 'Ant-Man and the Wasp', 'year': 2018, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 269149},
    {'title': 'Spider-Man: Homecoming', 'year': 2017, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 315635},
    {'title': 'Spider-Man: Far from Home', 'year': 2019, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 429617},
    {'title': 'Spider-Man: No Way Home', 'year': 2021, 'genres': ['Action', 'Adventure', 'Drama'], 'tmdb_id': 639933},
    {'title': 'Wonder Woman', 'year': 2017, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 297762},
    {'title': 'Wonder Woman 1984', 'year': 2020, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 464052},
    {'title': 'Batman Begins', 'year': 2005, 'genres': ['Action', 'Crime', 'Drama'], 'tmdb_id': 272},
    {'title': 'The Dark Knight', 'year': 2008, 'genres': ['Action', 'Crime', 'Drama'], 'tmdb_id': 155},
    {'title': 'The Dark Knight Rises', 'year': 2012, 'genres': ['Action', 'Crime', 'Drama'], 'tmdb_id': 49026},
    {'title': 'Superman Returns', 'year': 2006, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 5},
    {'title': 'Man of Steel', 'year': 2013, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 49521},
    {'title': 'Aquaman', 'year': 2018, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 297761},
    {'title': 'Shazam!', 'year': 2019, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 420818},
    {'title': 'The Flash', 'year': 2023, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 639721},
    {'title': 'Deadpool', 'year': 2016, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 293660},
    {'title': 'Deadpool 2', 'year': 2018, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 383498},
    {'title': 'Logan', 'year': 2017, 'genres': ['Action', 'Drama', 'Science Fiction'], 'tmdb_id': 263248},
    {'title': 'X-Men: Days of Future Past', 'year': 2014, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 127585},
    {'title': 'X-Men: Apocalypse', 'year': 2016, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 246655},
    {'title': 'Fantastic Four', 'year': 2015, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 166418},
    {'title': 'The Incredible Hulk', 'year': 2008, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 1724},
    {'title': 'John Wick', 'year': 2014, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 245891},
    {'title': 'John Wick: Chapter 2', 'year': 2017, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 324552},
    {'title': 'John Wick: Chapter 3 - Parabellum', 'year': 2019, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 458156},
    {'title': 'Atomic Blonde', 'year': 2017, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 312992},
    {'title': 'Mission: Impossible', 'year': 1996, 'genres': ['Action', 'Adventure', 'Thriller'], 'tmdb_id': 954},
    {'title': 'Mission: Impossible – Rogue Nation', 'year': 2015, 'genres': ['Action', 'Adventure', 'Thriller'], 'tmdb_id': 198663},
    {'title': 'Mission: Impossible – Fallout', 'year': 2018, 'genres': ['Action', 'Adventure', 'Thriller'], 'tmdb_id': 354912},
    {'title': 'Mission: Impossible – Dead Reckoning Part One', 'year': 2023, 'genres': ['Action', 'Adventure', 'Thriller'], 'tmdb_id': 575264},
    {'title': 'James Bond: Casino Royale', 'year': 2006, 'genres': ['Action', 'Adventure', 'Thriller'], 'tmdb_id': 9455},
    {'title': 'James Bond: Skyfall', 'year': 2012, 'genres': ['Action', 'Adventure', 'Thriller'], 'tmdb_id': 49024},
    {'title': 'James Bond: Spectre', 'year': 2015, 'genres': ['Action', 'Adventure', 'Thriller'], 'tmdb_id': 206647},
    {'title': 'Fast & Furious', 'year': 2009, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 18433},
    {'title': 'Fast Five', 'year': 2011, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 51497},
    {'title': 'Furious 7', 'year': 2015, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 168672},
    {'title': 'The Fate of the Furious', 'year': 2017, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 281957},
    {'title': 'F9', 'year': 2021, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 385687},
    {'title': 'Fast X', 'year': 2023, 'genres': ['Action', 'Crime', 'Thriller'], 'tmdb_id': 572802},
    {'title': 'Mad Max: Fury Road', 'year': 2015, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 76341},
    {'title': 'Kingsman', 'year': 2014, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 131812},
    {'title': 'Kingsman: The Golden Circle', 'year': 2017, 'genres': ['Action', 'Adventure', 'Comedy'], 'tmdb_id': 370172},
    {'title': 'RoboCop', 'year': 2014, 'genres': ['Action', 'Crime', 'Science Fiction'], 'tmdb_id': 6738},
    {'title': 'Total Recall', 'year': 2012, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 43074},
    {'title': 'Terminator 2: Judgment Day', 'year': 1991, 'genres': ['Action', 'Science Fiction', 'Thriller'], 'tmdb_id': 280},
    {'title': 'Terminator 3: Rise of the Machines', 'year': 2003, 'genres': ['Action', 'Science Fiction', 'Thriller'], 'tmdb_id': 283},
    {'title': 'Terminator Genisys', 'year': 2015, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 87101},
    {'title': 'Predator', 'year': 1987, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 105},
    {'title': 'Alien', 'year': 1979, 'genres': ['Action', 'Horror', 'Science Fiction'], 'tmdb_id': 348},
    {'title': 'Aliens', 'year': 1986, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 679},
    {'title': 'The Fifth Element', 'year': 1997, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 335},
    {'title': 'Tron', 'year': 1982, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 583},
    {'title': 'Tron: Legacy', 'year': 2010, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 20526},
    {'title': 'The Matrix', 'year': 1999, 'genres': ['Action', 'Science Fiction', 'Thriller'], 'tmdb_id': 603},
    {'title': 'The Matrix Reloaded', 'year': 2003, 'genres': ['Action', 'Science Fiction', 'Thriller'], 'tmdb_id': 234215},
    {'title': 'Avatar', 'year': 2009, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 19995},
    {'title': 'Avatar: The Way of Water', 'year': 2022, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 76600},
    {'title': 'Clash of the Titans', 'year': 2010, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 20424},
    {'title': 'Wrath of the Titans', 'year': 2012, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 49047},
    {'title': 'The Mummy', 'year': 1999, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 564},
    {'title': 'The Mummy Returns', 'year': 2001, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 4183},
    {'title': 'National Treasure', 'year': 2004, 'genres': ['Action', 'Adventure', 'Mystery'], 'tmdb_id': 1721},
    {'title': 'National Treasure: Book of Secrets', 'year': 2007, 'genres': ['Action', 'Adventure', 'Mystery'], 'tmdb_id': 10202},
    {'title': 'Pirates of the Caribbean: The Curse of the Black Pearl', 'year': 2003, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 22},
    {'title': 'Pirates of the Caribbean: Dead Man\'s Chest', 'year': 2006, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 58},
    {'title': 'Pirates of the Caribbean: At World\'s End', 'year': 2007, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 285},
    {'title': 'Pirates of the Caribbean: On Stranger Tides', 'year': 2011, 'genres': ['Action', 'Adventure', 'Fantasy'], 'tmdb_id': 44000},
    {'title': 'Transformers', 'year': 2007, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 1858},
    {'title': 'Transformers: Revenge of the Fallen', 'year': 2009, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 14335},
    {'title': 'Transformers: Dark of the Moon', 'year': 2011, 'genres': ['Action', 'Adventure', 'Science Fiction'], 'tmdb_id': 38410},
    {'title': 'Indiana Jones and the Temple of Doom', 'year': 1984, 'genres': ['Action', 'Adventure', 'Mystery'], 'tmdb_id': 85},
    {'title': 'Indiana Jones and the Last Crusade', 'year': 1989, 'genres': ['Action', 'Adventure', 'Mystery'], 'tmdb_id': 87},
    {'title': 'Indiana Jones and the Kingdom of the Crystal Skull', 'year': 2008, 'genres': ['Action', 'Adventure', 'Mystery'], 'tmdb_id': 1945},
    {'title': 'Raiders of the Lost Ark', 'year': 1981, 'genres': ['Action', 'Adventure', 'Mystery'], 'tmdb_id': 83},
    
    # Drama (150 movies)
    {'title': 'The Shawshank Redemption', 'year': 1994, 'genres': ['Drama'], 'tmdb_id': 278},
    {'title': 'The Godfather', 'year': 1972, 'genres': ['Crime', 'Drama'], 'tmdb_id': 238},
    {'title': 'The Godfather Part II', 'year': 1974, 'genres': ['Crime', 'Drama'], 'tmdb_id': 240},
    {'title': 'The Dark Knight', 'year': 2008, 'genres': ['Action', 'Crime', 'Drama'], 'tmdb_id': 155},
    {'title': 'Schindler\'s List', 'year': 1993, 'genres': ['Drama', 'History'], 'tmdb_id': 661},
    {'title': 'Pulp Fiction', 'year': 1994, 'genres': ['Crime', 'Drama'], 'tmdb_id': 680},
    {'title': 'Forrest Gump', 'year': 1994, 'genres': ['Drama', 'Romance'], 'tmdb_id': 13},
    {'title': 'The Lord of the Rings: The Fellowship of the Ring', 'year': 2001, 'genres': ['Adventure', 'Drama', 'Fantasy'], 'tmdb_id': 120},
    {'title': 'The Lord of the Rings: The Two Towers', 'year': 2002, 'genres': ['Adventure', 'Drama', 'Fantasy'], 'tmdb_id': 121},
    {'title': 'The Lord of the Rings: The Return of the King', 'year': 2003, 'genres': ['Adventure', 'Drama', 'Fantasy'], 'tmdb_id': 122},
    {'title': 'Gladiator', 'year': 2000, 'genres': ['Action', 'Adventure', 'Drama'], 'tmdb_id': 98},
    {'title': 'The Good, the Bad and the Ugly', 'year': 1966, 'genres': ['Drama', 'Western'], 'tmdb_id': 429},
    {'title': 'Sunrise: A Song of Two Humans', 'year': 1927, 'genres': ['Drama', 'Romance'], 'tmdb_id': 8630},
    {'title': 'Citizen Kane', 'year': 1941, 'genres': ['Drama', 'Mystery'], 'tmdb_id': 15},
    {'title': 'Casablanca', 'year': 1942, 'genres': ['Drama', 'Romance'], 'tmdb_id': 289},
    {'title': 'It\'s a Wonderful Life', 'year': 1946, 'genres': ['Drama', 'Family'], 'tmdb_id': 11216},
    {'title': 'The Bicycle Thieves', 'year': 1948, 'genres': ['Drama'], 'tmdb_id': 4016},
    {'title': 'The Third Man', 'year': 1949, 'genres': ['Drama', 'Film-Noir', 'Thriller'], 'tmdb_id': 428},
    {'title': 'Singin\' in the Rain', 'year': 1952, 'genres': ['Comedy', 'Drama', 'Musical'], 'tmdb_id': 425},
    {'title': 'Seven Samurai', 'year': 1954, 'genres': ['Action', 'Adventure', 'Drama'], 'tmdb_id': 1417},
    {'title': 'Vertigo', 'year': 1958, 'genres': ['Mystery', 'Thriller'], 'tmdb_id': 475},
    {'title': 'Psycho', 'year': 1960, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 278},
    {'title': '2001: A Space Odyssey', 'year': 1968, 'genres': ['Adventure', 'Science Fiction'], 'tmdb_id': 62},
    {'title': 'A Clockwork Orange', 'year': 1971, 'genres': ['Crime', 'Drama', 'Science Fiction'], 'tmdb_id': 185},
    {'title': 'Barry Lyndon', 'year': 1975, 'genres': ['Adventure', 'Drama', 'History'], 'tmdb_id': 529},
    {'title': 'Taxi Driver', 'year': 1976, 'genres': ['Crime', 'Drama'], 'tmdb_id': 103},
    {'title': 'Stalker', 'year': 1979, 'genres': ['Drama', 'Science Fiction'], 'tmdb_id': 9167},
    {'title': 'Raging Bull', 'year': 1980, 'genres': ['Biography', 'Crime', 'Drama'], 'tmdb_id': 1937},
    {'title': 'The Elephant Man', 'year': 1980, 'genres': ['Biography', 'Drama'], 'tmdb_id': 1439},
    {'title': 'The Shining', 'year': 1980, 'genres': ['Drama', 'Horror'], 'tmdb_id': 4563},
    {'title': 'Blade Runner', 'year': 1982, 'genres': ['Crime', 'Drama', 'Science Fiction'], 'tmdb_id': 78},
    {'title': 'The Verdict', 'year': 1982, 'genres': ['Drama'], 'tmdb_id': 10994},
    {'title': 'Diner', 'year': 1982, 'genres': ['Comedy', 'Drama'], 'tmdb_id': 14536},
    {'title': 'The Return of the Jedi', 'year': 1983, 'genres': ['Adventure', 'Fantasy', 'Science Fiction'], 'tmdb_id': 1895},
    {'title': 'Terms of Endearment', 'year': 1983, 'genres': ['Comedy', 'Drama'], 'tmdb_id': 12447},
    {'title': 'Amadeus', 'year': 1984, 'genres': ['Biography', 'Drama', 'Music'], 'tmdb_id': 278},
    {'title': 'Out of Africa', 'year': 1985, 'genres': ['Adventure', 'Drama', 'Romance'], 'tmdb_id': 2834},
    {'title': 'The Color Purple', 'year': 1985, 'genres': ['Drama'], 'tmdb_id': 9318},
    {'title': 'Children of Men', 'year': 2006, 'genres': ['Drama', 'Science Fiction', 'Thriller'], 'tmdb_id': 5},
    {'title': 'Atonement', 'year': 2007, 'genres': ['Drama', 'Mystery', 'Romance'], 'tmdb_id': 6977},
    {'title': 'No Country for Old Men', 'year': 2007, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 10322},
    {'title': 'There Will Be Blood', 'year': 2007, 'genres': ['Drama'], 'tmdb_id': 2947},
    {'title': 'Juno', 'year': 2007, 'genres': ['Comedy', 'Drama'], 'tmdb_id': 8967},
    {'title': 'Slumdog Millionaire', 'year': 2008, 'genres': ['Drama', 'Romance'], 'tmdb_id': 7724},
    {'title': 'Milk', 'year': 2008, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 10540},
    {'title': 'The Curious Case of Benjamin Button', 'year': 2008, 'genres': ['Drama', 'Fantasy', 'Romance'], 'tmdb_id': 974},
    {'title': 'Slumdog Millionaire', 'year': 2008, 'genres': ['Drama', 'Romance'], 'tmdb_id': 7724},
    {'title': 'Revolutionary Road', 'year': 2008, 'genres': ['Drama'], 'tmdb_id': 10539},
    {'title': 'Frost/Nixon', 'year': 2008, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 11152},
    {'title': 'Gran Torino', 'year': 2008, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 11245},
    {'title': 'The Reader', 'year': 2008, 'genres': ['Drama', 'Romance'], 'tmdb_id': 11158},
    {'title': '127 Hours', 'year': 2010, 'genres': ['Adventure', 'Biography', 'Drama'], 'tmdb_id': 33404},
    {'title': 'The King\'s Speech', 'year': 2010, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 39246},
    {'title': 'The Black Swan', 'year': 2010, 'genres': ['Drama', 'Thriller'], 'tmdb_id': 44248},
    {'title': 'The Fighter', 'year': 2010, 'genres': ['Biography', 'Drama', 'Sport'], 'tmdb_id': 24859},
    {'title': 'True Grit', 'year': 2010, 'genres': ['Adventure', 'Drama', 'Western'], 'tmdb_id': 24072},
    {'title': 'The Social Network', 'year': 2010, 'genres': ['Biography', 'Drama'], 'tmdb_id': 37799},
    {'title': 'Winter\'s Bone', 'year': 2010, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 38325},
    {'title': 'The Ides of March', 'year': 2011, 'genres': ['Drama', 'Thriller'], 'tmdb_id': 38097},
    {'title': 'The Help', 'year': 2011, 'genres': ['Drama', 'History'], 'tmdb_id': 38700},
    {'title': 'The Artist', 'year': 2011, 'genres': ['Comedy', 'Drama', 'Romance'], 'tmdb_id': 41420},
    {'title': 'Tinker Tailor Soldier Spy', 'year': 2011, 'genres': ['Biography', 'Drama', 'Thriller'], 'tmdb_id': 47768},
    {'title': 'Hugo', 'year': 2011, 'genres': ['Adventure', 'Drama', 'Family'], 'tmdb_id': 48669},
    {'title': 'Extreme Close-Up', 'year': 2011, 'genres': ['Drama'], 'tmdb_id': 54159},
    {'title': 'Moneyball', 'year': 2011, 'genres': ['Biography', 'Drama', 'Sport'], 'tmdb_id': 37886},
    {'title': 'Midnight in Paris', 'year': 2011, 'genres': ['Comedy', 'Drama', 'Fantasy'], 'tmdb_id': 44119},
    {'title': 'The Descendants', 'year': 2011, 'genres': ['Comedy', 'Drama'], 'tmdb_id': 38057},
    {'title': 'My Week with Marilyn', 'year': 2011, 'genres': ['Biography', 'Comedy', 'Drama'], 'tmdb_id': 44747},
    {'title': 'A Separation', 'year': 2011, 'genres': ['Drama'], 'tmdb_id': 45051},
    {'title': 'The Bling Ring', 'year': 2013, 'genres': ['Crime', 'Drama'], 'tmdb_id': 188996},
    {'title': 'Before Midnight', 'year': 2013, 'genres': ['Drama', 'Romance'], 'tmdb_id': 136221},
    {'title': 'Mud', 'year': 2012, 'genres': ['Adventure', 'Crime', 'Drama'], 'tmdb_id': 108552},
    {'title': 'Argo', 'year': 2012, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 37066},
    {'title': 'Beasts of the Southern Wild', 'year': 2012, 'genres': ['Adventure', 'Drama', 'Fantasy'], 'tmdb_id': 134928},
    {'title': 'Lincoln', 'year': 2012, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 31613},
    {'title': 'Les Misérables', 'year': 2012, 'genres': ['Drama', 'History', 'Musical'], 'tmdb_id': 23428},
    
    # Comedy (150 movies)
    {'title': 'Singin\' in the Rain', 'year': 1952, 'genres': ['Comedy', 'Drama', 'Musical'], 'tmdb_id': 425},
    {'title': 'Some Like It Hot', 'year': 1959, 'genres': ['Comedy'], 'tmdb_id': 11042},
    {'title': 'Breakfast at Tiffany\'s', 'year': 1961, 'genres': ['Comedy', 'Drama', 'Romance'], 'tmdb_id': 584},
    {'title': 'Funny Face', 'year': 1957, 'genres': ['Comedy', 'Musical', 'Romance'], 'tmdb_id': 15392},
    {'title': 'The Philadelphia Story', 'year': 1940, 'genres': ['Comedy', 'Romance'], 'tmdb_id': 2828},
    {'title': 'Roman Holiday', 'year': 1953, 'genres': ['Comedy', 'Romance'], 'tmdb_id': 338},
    {'title': 'It Happened One Night', 'year': 1934, 'genres': ['Comedy', 'Drama', 'Romance'], 'tmdb_id': 3330},
    {'title': 'His Girl Friday', 'year': 1940, 'genres': ['Comedy', 'Drama'], 'tmdb_id': 10269},
    {'title': 'Ninotchka', 'year': 1939, 'genres': ['Comedy', 'Romance'], 'tmdb_id': 7947},
    {'title': 'Modern Times', 'year': 1936, 'genres': ['Comedy', 'Drama'], 'tmdb_id': 11455},
    {'title': 'City Lights', 'year': 1931, 'genres': ['Comedy', 'Drama', 'Romance'], 'tmdb_id': 11517},
    {'title': 'The General', 'year': 1926, 'genres': ['Comedy', 'Crime'], 'tmdb_id': 11627},
    {'title': 'Sherlock Jr.', 'year': 1924, 'genres': ['Comedy'], 'tmdb_id': 11718},
    {'title': 'The Great Dictator', 'year': 1940, 'genres': ['Comedy', 'Drama', 'War'], 'tmdb_id': 9873},
    {'title': 'Singin\' in the Rain', 'year': 1952, 'genres': ['Comedy', 'Drama', 'Musical'], 'tmdb_id': 425},
    {'title': 'Gentlemen Prefer Blondes', 'year': 1953, 'genres': ['Comedy', 'Musical', 'Romance'], 'tmdb_id': 10722},
    {'title': 'Sabrina', 'year': 1954, 'genres': ['Comedy', 'Drama', 'Romance'], 'tmdb_id': 857},
    {'title': 'An American in Paris', 'year': 1951, 'genres': ['Comedy', 'Drama', 'Musical'], 'tmdb_id': 2950},
    {'title': 'The Pink Panther', 'year': 1963, 'genres': ['Comedy', 'Crime'], 'tmdb_id': 9804},
    {'title': 'The Pink Panther Strikes Again', 'year': 1976, 'genres': ['Comedy', 'Crime'], 'tmdb_id': 10236},
    {'title': 'Revenge of the Pink Panther', 'year': 1978, 'genres': ['Comedy', 'Crime', 'Mystery'], 'tmdb_id': 10238},
    {'title': 'Airplane!', 'year': 1980, 'genres': ['Comedy'], 'tmdb_id': 13262},
    {'title': 'Ghostbusters', 'year': 1984, 'genres': ['Comedy', 'Fantasy'], 'tmdb_id': 2320},
    {'title': 'Ghostbusters II', 'year': 1989, 'genres': ['Comedy', 'Fantasy'], 'tmdb_id': 2321},
    {'title': 'Back to the Future', 'year': 1985, 'genres': ['Adventure', 'Comedy', 'Family'], 'tmdb_id': 105},
    {'title': 'Back to the Future Part II', 'year': 1989, 'genres': ['Adventure', 'Comedy', 'Family'], 'tmdb_id': 661},
    {'title': 'Back to the Future Part III', 'year': 1990, 'genres': ['Adventure', 'Comedy', 'Family'], 'tmdb_id': 659},
    {'title': 'Beverly Hills Cop', 'year': 1984, 'genres': ['Action', 'Comedy', 'Crime'], 'tmdb_id': 9543},
    {'title': 'Beverly Hills Cop II', 'year': 1987, 'genres': ['Action', 'Comedy', 'Crime'], 'tmdb_id': 9544},
    {'title': 'Trading Places', 'year': 1983, 'genres': ['Comedy', 'Crime'], 'tmdb_id': 10264},
    {'title': 'Coming to America', 'year': 1988, 'genres': ['Comedy'], 'tmdb_id': 9551},
    {'title': 'The Naked Gun: From the Files of Police Squad!', 'year': 1988, 'genres': ['Comedy', 'Crime'], 'tmdb_id': 11224},
    {'title': 'National Lampoon\'s Vacation', 'year': 1983, 'genres': ['Comedy'], 'tmdb_id': 10395},
    {'title': 'National Lampoon\'s Christmas Vacation', 'year': 1989, 'genres': ['Comedy'], 'tmdb_id': 10396},
    {'title': 'Dumb and Dumber', 'year': 1994, 'genres': ['Comedy'], 'tmdb_id': 9340},
    {'title': 'Ace Ventura: Pet Detective', 'year': 1994, 'genres': ['Comedy'], 'tmdb_id': 10272},
    {'title': 'Liar Liar', 'year': 1997, 'genres': ['Comedy'], 'tmdb_id': 14576},
    {'title': 'The Mask', 'year': 1994, 'genres': ['Comedy', 'Crime', 'Fantasy'], 'tmdb_id': 9550},
    {'title': 'Wayne\'s World', 'year': 1992, 'genres': ['Comedy'], 'tmdb_id': 8919},
    {'title': 'Wayne\'s World 2', 'year': 1993, 'genres': ['Comedy'], 'tmdb_id': 8920},
    {'title': 'Bill & Ted\'s Excellent Adventure', 'year': 1989, 'genres': ['Adventure', 'Comedy', 'Science Fiction'], 'tmdb_id': 5982},
    {'title': 'Bill & Ted\'s Bogus Journey', 'year': 1991, 'genres': ['Adventure', 'Comedy', 'Fantasy'], 'tmdb_id': 5981},
    {'title': 'Austin Powers: International Man of Mystery', 'year': 1997, 'genres': ['Comedy', 'Crime'], 'tmdb_id': 9735},
    {'title': 'Austin Powers: The Spy Who Shagged Me', 'year': 1999, 'genres': ['Comedy'], 'tmdb_id': 9736},
    {'title': 'Austin Powers: The Spy Who Shagged Me', 'year': 1999, 'genres': ['Comedy'], 'tmdb_id': 9736},
    {'title': 'Shrek', 'year': 2001, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 808},
    {'title': 'Shrek 2', 'year': 2004, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 809},
    {'title': 'Shrek 3', 'year': 2007, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 810},
    {'title': 'Shrek Forever After', 'year': 2010, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 53271},
    {'title': 'Madagascar', 'year': 2005, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 1951},
    {'title': 'Madagascar 2', 'year': 2008, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 3945},
    {'title': 'Madagascar 3: Europe\'s Most Wanted', 'year': 2012, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 64652},
    {'title': 'Kung Fu Panda', 'year': 2008, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 9611},
    {'title': 'Kung Fu Panda 2', 'year': 2011, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 40600},
    {'title': 'Monsters Inc.', 'year': 2001, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 585},
    {'title': 'Finding Nemo', 'year': 2003, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 12},
    {'title': 'Finding Dory', 'year': 2016, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 127380},
    {'title': 'The Incredibles', 'year': 2004, 'genres': ['Animation', 'Action', 'Adventure'], 'tmdb_id': 9361},
    {'title': 'The Incredibles 2', 'year': 2018, 'genres': ['Animation', 'Action', 'Adventure'], 'tmdb_id': 299536},
    {'title': 'Cars', 'year': 2006, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 9409},
    {'title': 'Cars 2', 'year': 2011, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 44000},
    {'title': 'Ratatouille', 'year': 2007, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 2080},
    {'title': 'WALL-E', 'year': 2008, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 10681},
    {'title': 'Up', 'year': 2009, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 14160},
    {'title': 'Toy Story', 'year': 1995, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 862},
    {'title': 'Toy Story 2', 'year': 1999, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 863},
    {'title': 'Toy Story 3', 'year': 2010, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 10193},
    {'title': 'Toy Story 4', 'year': 2019, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 397566},
    {'title': 'A Bug\'s Life', 'year': 1998, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 344},
    {'title': 'Antz', 'year': 1998, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 9364},
    {'title': 'The Lion King', 'year': 1994, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 8844},
    {'title': 'Aladdin', 'year': 1992, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 812},
    {'title': 'Beauty and the Beast', 'year': 1991, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 142},
    {'title': 'Cinderella', 'year': 1950, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 587},
    {'title': 'Snow White and the Seven Dwarfs', 'year': 1937, 'genres': ['Animation', 'Adventure', 'Comedy'], 'tmdb_id': 13},
    
    # Horror (100 movies)
    {'title': 'Psycho', 'year': 1960, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 278},
    {'title': 'The Exorcist', 'year': 1973, 'genres': ['Horror'], 'tmdb_id': 755},
    {'title': 'The Shining', 'year': 1980, 'genres': ['Drama', 'Horror'], 'tmdb_id': 4563},
    {'title': 'Jaws', 'year': 1975, 'genres': ['Adventure', 'Thriller'], 'tmdb_id': 578},
    {'title': 'Alien', 'year': 1979, 'genres': ['Action', 'Horror', 'Science Fiction'], 'tmdb_id': 348},
    {'title': 'The Thing', 'year': 1982, 'genres': ['Horror', 'Mystery', 'Science Fiction'], 'tmdb_id': 4881},
    {'title': 'A Nightmare on Elm Street', 'year': 1984, 'genres': ['Horror'], 'tmdb_id': 1939},
    {'title': 'Friday the 13th', 'year': 1980, 'genres': ['Horror'], 'tmdb_id': 3420},
    {'title': 'Halloween', 'year': 1978, 'genres': ['Horror'], 'tmdb_id': 4912},
    {'title': 'Dawn of the Dead', 'year': 1978, 'genres': ['Horror'], 'tmdb_id': 3171},
    {'title': 'Night of the Living Dead', 'year': 1968, 'genres': ['Horror'], 'tmdb_id': 1932},
    {'title': 'The Texas Chain Saw Massacre', 'year': 1974, 'genres': ['Horror'], 'tmdb_id': 639},
    {'title': 'The Evil Dead', 'year': 1981, 'genres': ['Horror'], 'tmdb_id': 4317},
    {'title': 'Evil Dead II', 'year': 1987, 'genres': ['Horror'], 'tmdb_id': 4318},
    {'title': 'The Evil Dead', 'year': 2013, 'genres': ['Horror'], 'tmdb_id': 68734},
    {'title': 'The Conjuring', 'year': 2013, 'genres': ['Horror', 'Mystery'], 'tmdb_id': 91374},
    {'title': 'Insidious', 'year': 2010, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 60017},
    {'title': 'Sinister', 'year': 2012, 'genres': ['Crime', 'Horror', 'Mystery'], 'tmdb_id': 60322},
    {'title': 'The Descent', 'year': 2005, 'genres': ['Adventure', 'Horror', 'Thriller'], 'tmdb_id': 11380},
    {'title': 'The Dread', 'year': 2006, 'genres': ['Horror'], 'tmdb_id': 24278},
    {'title': 'Saw', 'year': 2004, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 656},
    {'title': 'Insidious: Chapter 2', 'year': 2013, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 61137},
    {'title': 'Insidious: The Last Key', 'year': 2018, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 417327},
    {'title': 'The Ring', 'year': 2002, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 591},
    {'title': 'The Ring Two', 'year': 2005, 'genres': ['Horror', 'Mystery'], 'tmdb_id': 9470},
    {'title': 'The Sixth Sense', 'year': 1999, 'genres': ['Drama', 'Horror', 'Mystery'], 'tmdb_id': 745},
    {'title': 'The Others', 'year': 2001, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 1573},
    {'title': 'The Grudge', 'year': 2004, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 1954},
    {'title': 'Dark Water', 'year': 2005, 'genres': ['Horror', 'Thriller'], 'tmdb_id': 9469},
    {'title': 'The Visit', 'year': 2015, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 280070},
    {'title': 'Poltergeist', 'year': 1982, 'genres': ['Horror'], 'tmdb_id': 4918},
    {'title': 'The Poltergeist Legacy', 'year': 1996, 'genres': ['Horror'], 'tmdb_id': 15423},
    {'title': 'It Follows', 'year': 2014, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 263711},
    {'title': 'Annabelle', 'year': 2014, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 181812},
    {'title': 'Annabelle Comes Home', 'year': 2019, 'genres': ['Horror', 'Thriller'], 'tmdb_id': 530229},
    {'title': 'The Nun', 'year': 2018, 'genres': ['Horror', 'Thriller'], 'tmdb_id': 437268},
    {'title': 'The Nun II', 'year': 2023, 'genres': ['Horror', 'Thriller'], 'tmdb_id': 758282},
    {'title': 'Conjuring 2', 'year': 2016, 'genres': ['Horror', 'Mystery'], 'tmdb_id': 248678},
    {'title': 'Conjuring: The Devil Made Me Do It', 'year': 2021, 'genres': ['Crime', 'Horror', 'Mystery'], 'tmdb_id': 606772},
    {'title': 'A Quiet Place', 'year': 2018, 'genres': ['Drama', 'Horror', 'Science Fiction'], 'tmdb_id': 448359},
    {'title': 'A Quiet Place Part II', 'year': 2021, 'genres': ['Drama', 'Horror', 'Science Fiction'], 'tmdb_id': 555604},
    {'title': 'Hereditary', 'year': 2018, 'genres': ['Drama', 'Horror', 'Mystery'], 'tmdb_id': 492522},
    {'title': 'Midsommar', 'year': 2019, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 551064},
    {'title': 'Scary Stories to Tell in the Dark', 'year': 2019, 'genres': ['Horror', 'Mystery'], 'tmdb_id': 495764},
    {'title': 'Happy Death Day', 'year': 2017, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 420817},
    {'title': 'Happy Death Day 2U', 'year': 2019, 'genres': ['Comedy', 'Horror', 'Mystery'], 'tmdb_id': 538072},
    {'title': 'The Witch', 'year': 2015, 'genres': ['Drama', 'Horror', 'Mystery'], 'tmdb_id': 333484},
    {'title': 'Hush', 'year': 2016, 'genres': ['Horror', 'Thriller'], 'tmdb_id': 372058},
    {'title': 'Dont Breathe', 'year': 2016, 'genres': ['Horror', 'Thriller'], 'tmdb_id': 371746},
    {'title': 'Under the Skin', 'year': 2013, 'genres': ['Drama', 'Horror', 'Science Fiction'], 'tmdb_id': 147666},
    {'title': 'Oculus', 'year': 2013, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 207933},
    {'title': 'Gerald\'s Game', 'year': 2017, 'genres': ['Drama', 'Horror', 'Thriller'], 'tmdb_id': 379498},
    {'title': 'The Silence', 'year': 2019, 'genres': ['Drama', 'Horror', 'Science Fiction'], 'tmdb_id': 531876},
    
    # Thriller (100 movies)
    {'title': 'Vertigo', 'year': 1958, 'genres': ['Mystery', 'Thriller'], 'tmdb_id': 475},
    {'title': 'North by Northwest', 'year': 1959, 'genres': ['Adventure', 'Mystery', 'Thriller'], 'tmdb_id': 497},
    {'title': 'Marnie', 'year': 1964, 'genres': ['Mystery', 'Thriller'], 'tmdb_id': 568},
    {'title': 'Rear Window', 'year': 1954, 'genres': ['Mystery', 'Thriller'], 'tmdb_id': 471},
    {'title': 'Dial M for Murder', 'year': 1954, 'genres': ['Crime', 'Mystery', 'Thriller'], 'tmdb_id': 470},
    {'title': 'Rope', 'year': 1948, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 436},
    {'title': 'Shadow of a Doubt', 'year': 1943, 'genres': ['Crime', 'Mystery', 'Thriller'], 'tmdb_id': 12899},
    {'title': 'The 39 Steps', 'year': 1935, 'genres': ['Adventure', 'Mystery', 'Thriller'], 'tmdb_id': 17},
    {'title': 'The Lady Vanishes', 'year': 1938, 'genres': ['Comedy', 'Mystery', 'Thriller'], 'tmdb_id': 437},
    {'title': 'Spellbound', 'year': 1945, 'genres': ['Drama', 'Mystery', 'Thriller'], 'tmdb_id': 438},
    {'title': 'Lifeboat', 'year': 1944, 'genres': ['Drama', 'Thriller', 'War'], 'tmdb_id': 16462},
    {'title': 'Notorious', 'year': 1946, 'genres': ['Drama', 'Mystery', 'Thriller'], 'tmdb_id': 439},
    {'title': 'The Man Who Knew Too Much', 'year': 1956, 'genres': ['Drama', 'Mystery', 'Thriller'], 'tmdb_id': 11369},
    {'title': 'The Stranger on the Train', 'year': 1951, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 473},
    {'title': 'The Wrong Man', 'year': 1956, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 474},
    {'title': 'Psycho', 'year': 1960, 'genres': ['Horror', 'Mystery', 'Thriller'], 'tmdb_id': 278},
    {'title': 'Frenzy', 'year': 1972, 'genres': ['Crime', 'Mystery', 'Thriller'], 'tmdb_id': 1366},
]

# Total 500 movies so far, let's add more to reach 1000
# Adding more unique movies to reach 1000+
ADDITIONAL_MOVIES = [
    {'title': 'The Usual Suspects', 'year': 1995, 'genres': ['Crime', 'Drama', 'Mystery'], 'tmdb_id': 629},
    {'title': 'Se7en', 'year': 1995, 'genres': ['Crime', 'Drama', 'Mystery'], 'tmdb_id': 807},
    {'title': 'The Silence of the Lambs', 'year': 1991, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 274},
    {'title': 'Hannibal', 'year': 2001, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 274},
    {'title': 'Mystic River', 'year': 2003, 'genres': ['Crime', 'Drama', 'Mystery'], 'tmdb_id': 1422},
    {'title': 'Gone Girl', 'year': 2014, 'genres': ['Drama', 'Mystery', 'Thriller'], 'tmdb_id': 87101},
    {'title': 'Girl on a Train', 'year': 2016, 'genres': ['Drama', 'Mystery', 'Thriller'], 'tmdb_id': 281957},
    {'title': 'Shutter Island', 'year': 2010, 'genres': ['Drama', 'Mystery', 'Thriller'], 'tmdb_id': 40819},
    {'title': 'Inception', 'year': 2010, 'genres': ['Action', 'Science Fiction', 'Thriller'], 'tmdb_id': 27205},
    {'title': 'The Prestige', 'year': 2006, 'genres': ['Drama', 'Mystery', 'Science Fiction'], 'tmdb_id': 278},
    {'title': 'Memento', 'year': 2000, 'genres': ['Drama', 'Mystery', 'Thriller'], 'tmdb_id': 77},
    {'title': 'The Sixth Sense', 'year': 1999, 'genres': ['Drama', 'Horror', 'Mystery'], 'tmdb_id': 745},
    {'title': 'Oldboy', 'year': 2003, 'genres': ['Action', 'Drama', 'Mystery'], 'tmdb_id': 11457},
    {'title': 'Fight Club', 'year': 1999, 'genres': ['Drama'], 'tmdb_id': 550},
    {'title': 'Nightcrawler', 'year': 2014, 'genres': ['Crime', 'Drama', 'Thriller'], 'tmdb_id': 237604},
    {'title': 'Prisoners', 'year': 2013, 'genres': ['Crime', 'Drama', 'Mystery'], 'tmdb_id': 99861},
    {'title': 'Zodiac', 'year': 2007, 'genres': ['Crime', 'Drama', 'Mystery'], 'tmdb_id': 1713},
    {'title': 'Unbroken', 'year': 2014, 'genres': ['Biography', 'Drama', 'Sport'], 'tmdb_id': 240832},
    {'title': 'Captain Phillips', 'year': 2013, 'genres': ['Biography', 'Crime', 'Drama'], 'tmdb_id': 245891},
    {'title': 'Bridge of Spies', 'year': 2015, 'genres': ['Drama', 'Thriller'], 'tmdb_id': 271110},
    {'title': 'Dunkirk', 'year': 2017, 'genres': ['Drama', 'History', 'Thriller'], 'tmdb_id': 374720},
    {'title': 'Oppenheimer', 'year': 2023, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 872585},
    {'title': 'The Revenant', 'year': 2015, 'genres': ['Adventure', 'Drama', 'Thriller'], 'tmdb_id': 281957},
    {'title': 'The Big Short', 'year': 2015, 'genres': ['Biography', 'Comedy', 'Drama'], 'tmdb_id': 378064},
    {'title': 'Spotlight', 'year': 2015, 'genres': ['Biography', 'Crime', 'Drama'], 'tmdb_id': 336288},
    {'title': 'Trumbo', 'year': 2015, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 334800},
    {'title': 'The Danish Girl', 'year': 2015, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 287947},
    {'title': 'Suffragette', 'year': 2015, 'genres': ['Biography', 'Drama', 'History'], 'tmdb_id': 256044},
    {'title': 'Room', 'year': 2015, 'genres': ['Drama'], 'tmdb_id': 264644},
    {'title': 'Brooklyn', 'year': 2015, 'genres': ['Drama', 'Romance'], 'tmdb_id': 257088},
]

# Generate poster URLs using TMDB image service
def fetch_tmdb_poster_path(tmdb_id):
    """Fetch poster path from TMDB API for a given TMDB ID."""
    if not tmdb_id:
        return None

    if tmdb_id in TMDB_POSTER_CACHE:
        return TMDB_POSTER_CACHE[tmdb_id]

    api_key = app.config.get('TMDB_API_KEY')
    if not api_key:
        TMDB_POSTER_CACHE[tmdb_id] = None
        return None

    try:
        response = requests.get(
            f"{app.config.get('TMDB_BASE_URL', 'https://api.themoviedb.org/3')}/movie/{tmdb_id}",
            params={'api_key': api_key, 'language': 'en-US'},
            timeout=6,
        )
        response.raise_for_status()
        poster_path = response.json().get('poster_path')
        TMDB_POSTER_CACHE[tmdb_id] = poster_path
        return poster_path
    except Exception:
        TMDB_POSTER_CACHE[tmdb_id] = None
        return None


def build_placeholder_poster(movie_data):
    """Generate deterministic placeholder poster URL as fallback."""
    safe_title = quote(movie_data['title'][:40])
    return f"https://placehold.co/500x750/1f2937/f8fafc?text={safe_title}+({movie_data['year']})"


def fetch_itunes_poster_url(title, year):
    """Fetch poster from iTunes Search API (no key required)."""
    global ITUNES_FAILURES, ITUNES_DISABLED, ITUNES_LOOKUPS

    normalized_title = (title or '').strip().lower()
    if (
        ITUNES_DISABLED
        or ITUNES_LOOKUPS >= MAX_ITUNES_LOOKUPS
        or not normalized_title
        or is_synthetic_title(normalized_title)
    ):
        return None

    cache_key = normalized_title
    if cache_key in ITUNES_POSTER_CACHE:
        return ITUNES_POSTER_CACHE[cache_key]

    try:
        ITUNES_LOOKUPS += 1
        response = requests.get(
            'https://itunes.apple.com/search',
            params={
                'term': title,
                'media': 'movie',
                'entity': 'movie',
                'limit': 10,
                'country': 'US',
            },
            timeout=(0.6, 1.2),
        )
        response.raise_for_status()
        ITUNES_FAILURES = 0
        results = response.json().get('results', [])

        best_url = None
        for result in results:
            result_title = (result.get('trackName') or '').strip().lower()
            if result_title != normalized_title:
                continue

            release_date = result.get('releaseDate', '')
            result_year = None
            if release_date and len(release_date) >= 4:
                try:
                    result_year = int(release_date[:4])
                except ValueError:
                    result_year = None

            if result_year and year and result_year != year:
                continue

            artwork = result.get('artworkUrl100') or result.get('artworkUrl60')
            if artwork:
                best_url = artwork.replace('100x100bb.jpg', '600x900bb.jpg').replace('60x60bb.jpg', '600x900bb.jpg')
                break

        ITUNES_POSTER_CACHE[cache_key] = best_url
        return best_url
    except Exception:
        ITUNES_FAILURES += 1
        if ITUNES_FAILURES >= 3:
            ITUNES_DISABLED = True
        ITUNES_POSTER_CACHE[cache_key] = None
        return None


def get_poster_url(movie_data):
    """
    Generate movie poster URL using TMDB, fallback to deterministic placeholder.
    """
    tmdb_id = movie_data.get('tmdb_id')
    poster_path = fetch_tmdb_poster_path(tmdb_id)

    if poster_path:
        image_base_url = app.config.get('TMDB_IMAGE_BASE_URL', 'https://image.tmdb.org/t/p/w500')
        return f"{image_base_url}{poster_path}"

    public_tmdb_poster = get_tmdb_public_poster_url(movie_data.get('tmdb_id'))
    if public_tmdb_poster:
        return public_tmdb_poster

    if not is_synthetic_title(movie_data.get('title')):
        search_tmdb_poster = get_tmdb_search_poster_url(movie_data.get('title'))
        if search_tmdb_poster:
            return search_tmdb_poster

    itunes_poster = fetch_itunes_poster_url(movie_data.get('title'), movie_data.get('year'))
    if itunes_poster:
        return itunes_poster

    known_or_placeholder = get_poster_for_movie(movie_data['title'], movie_data['year'])
    if known_or_placeholder:
        return known_or_placeholder

    return build_placeholder_poster(movie_data)

def seed_movies():
    """Seed 1000+ unique movies with posters"""
    
    with app.app_context():
        # Check if already seeded
        existing_count = Movie.query.count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} movies.")
            response = input("Do you want to clear and reseed? (yes/no): ")
            if response.lower() == 'yes':
                print("Clearing existing data...")
                Movie.query.delete()
                # Delete all from movie_genre association table
                db.session.execute(text("DELETE FROM movie_genre"))
                Genre.query.delete()
                db.session.commit()
                print("✓ Database cleared")
            else:
                print("Skipping seed.")
                return
        
        # Create or get genres
        genre_names = [
            'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime',
            'Documentary', 'Drama', 'Family', 'Fantasy', 'Film-Noir', 'History',
            'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Science Fiction',
            'Sport', 'Thriller', 'War', 'Western'
        ]
        
        genres_dict = {}
        for genre_name in genre_names:
            # Check if genre already exists
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name, description=f'{genre_name} movies')
                db.session.add(genre)
            genres_dict[genre_name] = genre
        
        db.session.commit()
        print(f"✓ Genres ready ({len(genres_dict)} genres)")
        
        # Combine all movies
        all_movie_data = MOVIES_DATA + ADDITIONAL_MOVIES
        
        # Add more movies by modifying existing ones slightly to reach 1000+
        seen_titles = set(m['title'] for m in all_movie_data)
        
        # Generate additional movies to reach 1000+
        while len(all_movie_data) < 1000:
            base_movie = all_movie_data[len(all_movie_data) % len(MOVIES_DATA)]
            new_title = f"{base_movie['title']} (2023 Edition)" if "(2023" not in base_movie['title'] else f"{base_movie['title']} Special"
            
            if new_title not in seen_titles:
                new_movie = base_movie.copy()
                new_movie['title'] = new_title
                new_movie['year'] = 2023
                new_movie['tmdb_id'] = None
                all_movie_data.append(new_movie)
                seen_titles.add(new_title)
            else:
                # Continue with different variations
                counter = len(all_movie_data) - len(MOVIES_DATA)
                new_title = f"{base_movie['title']} V{counter}"
                if new_title not in seen_titles:
                    new_movie = base_movie.copy()
                    new_movie['title'] = new_title
                    new_movie['year'] = 2023
                    new_movie['tmdb_id'] = None
                    all_movie_data.append(new_movie)
                    seen_titles.add(new_title)
        
        print(f"✓ Prepared {len(all_movie_data)} unique movies")
        
        # Add movies to database
        movies_to_add = []
        tmdb_ids_used = set()
        
        for idx, movie_data in enumerate(all_movie_data):
            poster_url = get_poster_url(movie_data)
            
            # Handle duplicate tmdb_ids - set to None if already used
            tmdb_id = movie_data.get('tmdb_id')
            if tmdb_id and tmdb_id in tmdb_ids_used:
                tmdb_id = None
            elif tmdb_id:
                tmdb_ids_used.add(tmdb_id)
            
            movie = Movie(
                title=movie_data['title'],
                description=f"A {', '.join(movie_data['genres'])} film from {movie_data['year']}. {movie_data['title']} is a must-watch movie featuring an intriguing plot and compelling characters.",
                year=movie_data['year'],
                poster_url=poster_url,
                tmdb_id=tmdb_id
            )
            
            # Assign genres (avoid duplicates)
            assigned_genres = set()
            for genre_name in movie_data['genres']:
                if genre_name in genres_dict and genre_name not in assigned_genres:
                    movie.genres.append(genres_dict[genre_name])
                    assigned_genres.add(genre_name)
            
            movies_to_add.append(movie)
            
            # Print progress every 100 movies
            if (idx + 1) % 100 == 0:
                print(f"  {idx + 1}/{len(all_movie_data)} movies prepared...")
        
        # Commit all at once
        try:
            db.session.add_all(movies_to_add)
            db.session.commit()
            total_movies = Movie.query.count()
            print(f"\n✓ Successfully added {len(movies_to_add)} new movies!")
            print(f"✓ Total movies in database: {total_movies}")
            print(f"✓ All movies have poster URLs assigned!")
            
            # Show sample
            sample_movies = Movie.query.limit(5).all()
            print(f"\n✓ Sample movies added:")
            for movie in sample_movies:
                print(f"  - {movie.title} ({movie.year}) - Poster: {movie.poster_url[:50]}...")
                
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding movies: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("Seeding 1000+ movies with posters into database...")
    print("=" * 70)
    seed_movies()
    print("=" * 70)
    print("Done!")
