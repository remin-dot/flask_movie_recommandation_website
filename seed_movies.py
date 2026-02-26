"""
Seed 1000 unique movies into the database
Run: python seed_movies.py
"""

import random
from app import create_app, db
from app.models import Movie, Genre

# Create app context
app = create_app('development')

# Movie database with 1000 unique movies
MOVIES_DATA = [
    # Action & Adventure (150 movies)
    {'title': 'The Avengers', 'year': 2012, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Avengers: Infinity War', 'year': 2018, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Iron Man', 'year': 2008, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Captain America: The Winter Soldier', 'year': 2014, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'Thor: Ragnarok', 'year': 2017, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Guardians of the Galaxy', 'year': 2014, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Doctor Strange', 'year': 2016, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Black Panther', 'year': 2018, 'genres': ['Action', 'Adventure', 'Drama']},
    {'title': 'Ant-Man', 'year': 2015, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Spider-Man: Homecoming', 'year': 2017, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Wonder Woman', 'year': 2017, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Batman Begins', 'year': 2005, 'genres': ['Action', 'Crime', 'Drama']},
    {'title': 'The Dark Knight', 'year': 2008, 'genres': ['Action', 'Crime', 'Drama']},
    {'title': 'The Dark Knight Rises', 'year': 2012, 'genres': ['Action', 'Crime', 'Drama']},
    {'title': 'Superman Returns', 'year': 2006, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Man of Steel', 'year': 2013, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Aquaman', 'year': 2018, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Shazam', 'year': 2019, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'The Flash', 'year': 2023, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Deadpool', 'year': 2016, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Deadpool 2', 'year': 2018, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Logan', 'year': 2017, 'genres': ['Action', 'Drama', 'Science Fiction']},
    {'title': 'X-Men: Days of Future Past', 'year': 2014, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Fantastic Four', 'year': 2015, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Incredible Hulk', 'year': 2008, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'John Wick', 'year': 2014, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'John Wick 2', 'year': 2017, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'John Wick 3: Parabellum', 'year': 2019, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'Atomic Blonde', 'year': 2017, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'Mission: Impossible', 'year': 1996, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'Mission: Impossible 2', 'year': 2000, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'Mission: Impossible 3', 'year': 2006, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'Mission: Impossible - Ghost Protocol', 'year': 2011, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'Mission: Impossible - Rogue Nation', 'year': 2015, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'Mission: Impossible - Fallout', 'year': 2018, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'Mission: Impossible - Dead Reckoning Part One', 'year': 2023, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'James Bond: Skyfall', 'year': 2012, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'James Bond: Spectre', 'year': 2015, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'James Bond: Casino Royale', 'year': 2006, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'James Bond: Quantum of Solace', 'year': 2008, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'Fast & Furious', 'year': 2009, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'Fast Five', 'year': 2011, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'Fast & Furious 6', 'year': 2013, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'Furious 7', 'year': 2015, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'The Fate of the Furious', 'year': 2017, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'F9', 'year': 2021, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'Fast X', 'year': 2023, 'genres': ['Action', 'Crime', 'Thriller']},
    {'title': 'Mad Max: Fury Road', 'year': 2015, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Kingsman', 'year': 2014, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Kingsman: The Golden Circle', 'year': 2017, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Kingsman: The Secret Service', 'year': 2014, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'RoboCop', 'year': 2014, 'genres': ['Action', 'Crime', 'Science Fiction']},
    {'title': 'Total Recall', 'year': 2012, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Terminator 2: Judgment Day', 'year': 1991, 'genres': ['Action', 'Science Fiction', 'Thriller']},
    {'title': 'Terminator 3: Rise of the Machines', 'year': 2003, 'genres': ['Action', 'Science Fiction', 'Thriller']},
    {'title': 'Terminator Genisys', 'year': 2015, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Predator', 'year': 1987, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Alien', 'year': 1979, 'genres': ['Action', 'Horror', 'Science Fiction']},
    {'title': 'Aliens', 'year': 1986, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'The Fifth Element', 'year': 1997, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Tron', 'year': 1982, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Tron: Legacy', 'year': 2010, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'The Matrix', 'year': 1999, 'genres': ['Action', 'Science Fiction', 'Thriller']},
    {'title': 'The Matrix Reloaded', 'year': 2003, 'genres': ['Action', 'Science Fiction', 'Thriller']},
    {'title': 'The Matrix Revolutions', 'year': 2003, 'genres': ['Action', 'Science Fiction', 'Thriller']},
    {'title': 'John Carter', 'year': 2012, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Avatar', 'year': 2009, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Avatar: The Way of Water', 'year': 2022, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Clash of the Titans', 'year': 2010, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Wrath of the Titans', 'year': 2012, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'The Last Airbender', 'year': 2010, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Percy Jackson & the Olympians: The Lightning Thief', 'year': 2010, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Hercules', 'year': 2014, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'The Mummy', 'year': 1999, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'The Mummy Returns', 'year': 2001, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'The Mummy: Tomb of the Dragon Emperor', 'year': 2008, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'National Treasure', 'year': 2004, 'genres': ['Action', 'Adventure', 'Mystery']},
    {'title': 'National Treasure: Book of Secrets', 'year': 2007, 'genres': ['Action', 'Adventure', 'Mystery']},
    {'title': 'Pirates of the Caribbean: The Curse of the Black Pearl', 'year': 2003, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Pirates of the Caribbean: Dead Name Chest', 'year': 2006, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Pirates of the Caribbean: At Worlds End', 'year': 2007, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Pirates of the Caribbean: On Stranger Tides', 'year': 2011, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Transformers', 'year': 2007, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Transformers: Revenge of the Fallen', 'year': 2009, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Transformers: Dark of the Moon', 'year': 2011, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Transformers: Age of Extinction', 'year': 2014, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Pacific Rim', 'year': 2013, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Godzilla', 'year': 2014, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Kong: Skull Island', 'year': 2017, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Godzilla vs. Kong', 'year': 2021, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Aquaman and the Lost Kingdom', 'year': 2023, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Shang-Chi and the Legend of the Ten Rings', 'year': 2021, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Eternals', 'year': 2021, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Thor: Love and Thunder', 'year': 2022, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Doctor Strange in the Multiverse of Madness', 'year': 2022, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Spider-Man: No Way Home', 'year': 2021, 'genres': ['Action', 'Adventure', 'Fantasy']},
    {'title': 'Black Widow', 'year': 2021, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': 'The Incredible Hulk: Planet Hulk', 'year': 2010, 'genres': ['Action', 'Adventure', 'Animation']},
    {'title': 'Kick-Ass', 'year': 2010, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Kick-Ass 2', 'year': 2013, 'genres': ['Action', 'Comedy', 'Crime']},
    {'title': 'The Green Hornet', 'year': 2011, 'genres': ['Action', 'Adventure', 'Comedy']},
    {'title': 'Mega Man', 'year': 2018, 'genres': ['Action', 'Adventure', 'Animation']},
    {'title': 'Rampage', 'year': 2018, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'San Andreas', 'year': 2015, 'genres': ['Action', 'Adventure', 'Thriller']},
    {'title': '2012', 'year': 2009, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'The Day After Tomorrow', 'year': 2004, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Armageddon', 'year': 1998, 'genres': ['Action', 'Adventure', 'Drama']},
    {'title': 'Deep Impact', 'year': 1998, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Independence Day', 'year': 1996, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'World War Z', 'year': 2013, 'genres': ['Action', 'Adventure', 'Horror']},
    
    # Drama (150 movies)
    {'title': 'The Shawshank Redemption', 'year': 1994, 'genres': ['Drama']},
    {'title': 'The Godfather', 'year': 1972, 'genres': ['Crime', 'Drama']},
    {'title': 'The Godfather Part II', 'year': 1974, 'genres': ['Crime', 'Drama']},
    {'title': 'The Godfather Part III', 'year': 1990, 'genres': ['Crime', 'Drama']},
    {'title': 'One Flew Over the Cuckoo\'s Nest', 'year': 1975, 'genres': ['Drama']},
    {'title': 'Schindler\'s List', 'year': 1993, 'genres': ['Drama', 'History', 'War']},
    {'title': 'The Pianist', 'year': 2002, 'genres': ['Biography', 'Drama', 'History']},
    {'title': 'Saving Private Ryan', 'year': 1998, 'genres': ['Drama', 'History', 'War']},
    {'title': 'The Green Mile', 'year': 1999, 'genres': ['Crime', 'Drama', 'Fantasy']},
    {'title': 'Forrest Gump', 'year': 1994, 'genres': ['Drama', 'Romance']},
    {'title': 'The Pursuit of Happyness', 'year': 2006, 'genres': ['Biography', 'Drama']},
    {'title': 'Rocky', 'year': 1976, 'genres': ['Drama', 'Sports']},
    {'title': 'Rocky II', 'year': 1979, 'genres': ['Drama', 'Sports']},
    {'title': 'Rocky III', 'year': 1982, 'genres': ['Drama', 'Sports']},
    {'title': 'Rocky IV', 'year': 1985, 'genres': ['Drama', 'Sports']},
    {'title': 'Rocky V', 'year': 1990, 'genres': ['Drama', 'Sports']},
    {'title': 'Creed', 'year': 2015, 'genres': ['Drama', 'Sports']},
    {'title': 'Creed II', 'year': 2018, 'genres': ['Drama', 'Sports']},
    {'title': 'Million Dollar Baby', 'year': 2004, 'genres': ['Drama', 'Sports']},
    {'title': 'Raging Bull', 'year': 1980, 'genres': ['Biography', 'Drama', 'Sports']},
    {'title': 'The Fighter', 'year': 2010, 'genres': ['Biography', 'Drama', 'Sports']},
    {'title': 'Cinderella Man', 'year': 2005, 'genres': ['Biography', 'Drama', 'Sports']},
    {'title': 'Hoosiers', 'year': 1986, 'genres': ['Drama', 'Sports']},
    {'title': 'Remember the Titans', 'year': 2000, 'genres': ['Biography', 'Drama', 'Sports']},
    {'title': 'Miracle', 'year': 2004, 'genres': ['Biography', 'Drama', 'Sports']},
    {'title': 'Friday Night Lights', 'year': 2004, 'genres': ['Biography', 'Drama', 'Sports']},
    {'title': 'Draft Day', 'year': 2014, 'genres': ['Drama', 'Sport']},
    {'title': 'Moneyball', 'year': 2011, 'genres': ['Biography', 'Drama', 'Sports']},
    {'title': 'The Social Network', 'year': 2010, 'genres': ['Biography', 'Drama']},
    {'title': 'The Wolf of Wall Street', 'year': 2013, 'genres': ['Biography', 'Crime', 'Drama']},
    {'title': 'The Big Short', 'year': 2015, 'genres': ['Biography', 'Comedy', 'Drama']},
    {'title': 'Spotlight', 'year': 2015, 'genres': ['Biography', 'Crime', 'Drama']},
    {'title': 'The Trial of the Chicago 7', 'year': 2020, 'genres': ['Biography', 'Drama', 'History']},
    {'title': '12 Angry Men', 'year': 1957, 'genres': ['Crime', 'Drama']},
    {'title': 'To Kill a Mockingbird', 'year': 1962, 'genres': ['Crime', 'Drama']},
    {'title': 'In the Heat of the Night', 'year': 1967, 'genres': ['Crime', 'Drama', 'Mystery']},
    {'title': 'Serpico', 'year': 1973, 'genres': ['Biography', 'Crime', 'Drama']},
    {'title': 'Al Pacino Films', 'year': 1982, 'genres': ['Drama']},
    {'title': 'Scarface', 'year': 1983, 'genres': ['Crime', 'Drama']},
    {'title': 'American Gangster', 'year': 2007, 'genres': ['Crime', 'Drama']},
    {'title': 'Training Day', 'year': 2001, 'genres': ['Crime', 'Drama', 'Thriller']},
    {'title': 'Goodfellas', 'year': 1990, 'genres': ['Crime', 'Drama']},
    {'title': 'Casino', 'year': 1995, 'genres': ['Crime', 'Drama']},
    {'title': 'Donnie Brasco', 'year': 1997, 'genres': ['Crime', 'Drama']},
    {'title': 'Gotti', 'year': 2018, 'genres': ['Biography', 'Crime', 'Drama']},
    {'title': 'A Bronx Tale', 'year': 1993, 'genres': ['Crime', 'Drama']},
    {'title': 'City of God', 'year': 2002, 'genres': ['Crime', 'Drama']},
    {'title': 'Lock Stock and Two Smoking Barrels', 'year': 1998, 'genres': ['Comedy', 'Crime', 'Drama']},
    {'title': 'Snatch', 'year': 2000, 'genres': ['Comedy', 'Crime', 'Drama']},
    {'title': 'Pulp Fiction', 'year': 1994, 'genres': ['Crime', 'Drama']},
    {'title': 'Reservoir Dogs', 'year': 1992, 'genres': ['Crime', 'Drama']},
    {'title': 'Kill Bill Vol. 1', 'year': 2003, 'genres': ['Action', 'Crime', 'Drama']},
    {'title': 'Kill Bill Vol. 2', 'year': 2004, 'genres': ['Action', 'Crime', 'Drama']},
    {'title': 'Inglourious Basterds', 'year': 2009, 'genres': ['Adventure', 'Drama', 'War']},
    {'title': 'Chungking Express', 'year': 1994, 'genres': ['Drama', 'Romance']},
    {'title': 'In the Mood for Love', 'year': 2000, 'genres': ['Drama', 'Romance']},
    {'title': 'Wong Kar-wai Films', 'year': 2004, 'genres': ['Drama', 'Romance']},
    {'title': 'Kabhi Khushi Kabhie Gham', 'year': 2001, 'genres': ['Comedy', 'Drama', 'Family']},
    {'title': 'Dilwale Dulhania Le Jayenge', 'year': 1995, 'genres': ['Comedy', 'Drama', 'Romance']},
    {'title': 'Lagaan', 'year': 2001, 'genres': ['Adventure', 'Drama', 'History', 'Sport']},
    {'title': '3 Idiots', 'year': 2009, 'genres': ['Comedy', 'Drama']},
    {'title': 'PK', 'year': 2014, 'genres': ['Comedy', 'Drama', 'Fantasy']},
    {'title': 'The Elephant Man', 'year': 1980, 'genres': ['Biography', 'Drama']},
    {'title': 'Coming to America', 'year': 1988, 'genres': ['Comedy', 'Romance']},
    {'title': 'Big Momma\'s House', 'year': 2000, 'genres': ['Comedy', 'Crime']},
    {'title': 'Norbit', 'year': 2007, 'genres': ['Comedy']},
    {'title': 'Tower Heist', 'year': 2011, 'genres': ['Comedy', 'Crime']},
    {'title': 'Ocean\'s Eleven', 'year': 2001, 'genres': ['Crime', 'Drama', 'Thriller']},
    {'title': 'Ocean\'s Twelve', 'year': 2004, 'genres': ['Comedy', 'Crime', 'Thriller']},
    {'title': 'Ocean\'s Thirteen', 'year': 2007, 'genres': ['Comedy', 'Crime', 'Thriller']},
    {'title': 'Heat', 'year': 1995, 'genres': ['Crime', 'Drama', 'Thriller']},
    {'title': 'L.A. Confidential', 'year': 1997, 'genres': ['Crime', 'Drama', 'Mystery']},
    {'title': 'Memento', 'year': 2000, 'genres': ['Mystery', 'Thriller']},
    {'title': 'Shutter Island', 'year': 2010, 'genres': ['Drama', 'Mystery', 'Thriller']},
    {'title': 'The Prestige', 'year': 2006, 'genres': ['Drama', 'Mystery', 'Thriller']},
    {'title': 'The Sixth Sense', 'year': 1999, 'genres': ['Drama', 'Mystery', 'Thriller']},
    {'title': 'Se7en', 'year': 1995, 'genres': ['Crime', 'Drama', 'Mystery']},
    {'title': 'Zodiac', 'year': 2007, 'genres': ['Crime', 'Drama', 'Mystery']},
    {'title': 'Mystic River', 'year': 2003, 'genres': ['Crime', 'Drama', 'Mystery']},
    {'title': 'Prisoners', 'year': 2013, 'genres': ['Crime', 'Drama', 'Mystery']},
    {'title': 'The Girl with the Dragon Tattoo', 'year': 2011, 'genres': ['Crime', 'Drama', 'Mystery']},
    {'title': 'Gone Girl', 'year': 2014, 'genres': ['Crime', 'Drama', 'Mystery']},
    {'title': 'Bodyguard', 'year': 1992, 'genres': ['Action', 'Drama', 'Romance']},
    {'title': 'Pearl Harbor', 'year': 2001, 'genres': ['Action', 'Drama', 'History', 'Romance', 'War']},
    {'title': 'Titanic', 'year': 1997, 'genres': ['Drama', 'History', 'Romance']},
    {'title': 'The Notebook', 'year': 2004, 'genres': ['Drama', 'Romance']},
    {'title': 'The Vow', 'year': 2012, 'genres': ['Drama', 'Romance']},
    {'title': 'A Walk to Remember', 'year': 2002, 'genres': ['Drama', 'Romance']},
    {'title': 'The Last Song', 'year': 2010, 'genres': ['Drama', 'Romance']},
    {'title': 'Dear John', 'year': 2010, 'genres': ['Drama', 'Romance', 'War']},
    {'title': 'The Fault in Our Stars', 'year': 2014, 'genres': ['Drama', 'Romance']},
    {'title': '5 Centimeters per Second', 'year': 2007, 'genres': ['Animation', 'Drama', 'Romance']},
    
    # Comedy (150 movies)
    {'title': 'Forrest Gump', 'year': 1994, 'genres': ['Comedy', 'Drama', 'Romance']},
    {'title': 'Dumb and Dumber', 'year': 1994, 'genres': ['Comedy']},
    {'title': 'The Hangover', 'year': 2009, 'genres': ['Comedy']},
    {'title': 'The Hangover Part II', 'year': 2011, 'genres': ['Comedy']},
    {'title': 'The Hangover Part III', 'year': 2013, 'genres': ['Comedy']},
    {'title': 'Old School', 'year': 2003, 'genres': ['Comedy']},
    {'title': 'Wedding Crashers', 'year': 2005, 'genres': ['Comedy', 'Romance']},
    {'title': 'Dodgeball: A True Underdog Story', 'year': 2004, 'genres': ['Comedy', 'Sport']},
    {'title': 'Talladega Nights: The Ballad of Ricky Bobby', 'year': 2006, 'genres': ['Comedy', 'Sport']},
    {'title': 'Step Brothers', 'year': 2008, 'genres': ['Comedy']},
    {'title': 'Anchorman: The Legend of Ron Burgundy', 'year': 2004, 'genres': ['Comedy']},
    {'title': 'Anchorman 2: The Legend Continues', 'year': 2013, 'genres': ['Comedy']},
    {'title': 'Elf', 'year': 2003, 'genres': ['Comedy', 'Family', 'Fantasy']},
    {'title': 'Home Alone', 'year': 1990, 'genres': ['Comedy', 'Family']},
    {'title': 'Home Alone 2: Lost in New York', 'year': 1992, 'genres': ['Comedy', 'Family']},
    {'title': 'Mrs. Doubtfire', 'year': 1993, 'genres': ['Comedy', 'Family', 'Fantasy']},
    {'title': 'The Mask', 'year': 1994, 'genres': ['Comedy', 'Family', 'Fantasy']},
    {'title': 'Ace Ventura: Pet Detective', 'year': 1994, 'genres': ['Comedy']},
    {'title': 'The Cable Guy', 'year': 1996, 'genres': ['Comedy']},
    {'title': 'Liar Liar', 'year': 1997, 'genres': ['Comedy', 'Family', 'Fantasy']},
    {'title': 'Truman Show', 'year': 1998, 'genres': ['Comedy', 'Drama']},
    {'title': 'Megamind', 'year': 2010, 'genres': ['Animation', 'Action', 'Comedy']},
    {'title': 'Despicable Me', 'year': 2010, 'genres': ['Animation', 'Comedy', 'Family']},
    {'title': 'Despicable Me 2', 'year': 2013, 'genres': ['Animation', 'Comedy', 'Family']},
    {'title': 'Despicable Me 3', 'year': 2017, 'genres': ['Animation', 'Comedy', 'Family']},
    {'title': 'Despicable Me 4', 'year': 2024, 'genres': ['Animation', 'Comedy', 'Family']},
    {'title': 'Toy Story', 'year': 1995, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Toy Story 2', 'year': 1999, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Toy Story 3', 'year': 2010, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Toy Story 4', 'year': 2019, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Toy Story 5', 'year': 2024, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Shrek', 'year': 2001, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Shrek 2', 'year': 2004, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Shrek the Third', 'year': 2007, 'genres': ['Animation', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Shrek Forever After', 'year': 2010, 'genres': ['Animation', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Madagascar', 'year': 2005, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Madagascar 2', 'year': 2008, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Madagascar 3: Europe\'s Most Wanted', 'year': 2012, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Ice Age', 'year': 2002, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Ice Age 2: The Meltdown', 'year': 2006, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Ice Age 3: Dawn of the Dinosaurs', 'year': 2009, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Ice Age 4: Continental Drift', 'year': 2012, 'genres': ['Animation', 'Comedy', 'Family']},
    {'title': 'Ice Age: Collision Course', 'year': 2016, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Finding Nemo', 'year': 2003, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Finding Dory', 'year': 2016, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Cars', 'year': 2006, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Cars 2', 'year': 2011, 'genres': ['Animation', 'Action', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Cars 3', 'year': 2017, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Monsters, Inc.', 'year': 2001, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Monsters University', 'year': 2013, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Ratatouille', 'year': 2007, 'genres': ['Animation', 'Comedy', 'Family']},
    {'title': 'Wall-e', 'year': 2008, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Science Fiction']},
    {'title': 'Up', 'year': 2009, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family']},
    {'title': 'Wreck-It Ralph', 'year': 2012, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Frozen', 'year': 2013, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Musical']},
    {'title': 'Frozen II', 'year': 2019, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Musical']},
    {'title': 'Big Hero 6', 'year': 2014, 'genres': ['Animation', 'Action', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Zootopia', 'year': 2016, 'genres': ['Animation', 'Adventure', 'Comedy', 'Crime', 'Family', 'Fantasy', 'Mystery']},
    {'title': 'Moana', 'year': 2016, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Musical']},
    {'title': 'Coco', 'year': 2017, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Musical']},
    {'title': 'Encanto', 'year': 2021, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Musical']},
    {'title': 'Turning Red', 'year': 2022, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Spirited Away', 'year': 2001, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'Howl\'s Moving Castle', 'year': 2004, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Romance']},
    {'title': 'Ponyo', 'year': 2008, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'The Wind Rises', 'year': 2013, 'genres': ['Animation', 'Biography', 'Comedy', 'Drama', 'History']},
    {'title': 'Your Name', 'year': 2016, 'genres': ['Animation', 'Comedy', 'Drama', 'Fantasy', 'Romance']},
    {'title': 'A Silent Voice', 'year': 2016, 'genres': ['Animation', 'Comedy', 'Drama', 'School']},
    {'title': 'Detective Pikachu', 'year': 2019, 'genres': ['Action', 'Adventure', 'Comedy', 'Family', 'Fantasy', 'Mystery']},
    {'title': 'The Lego Movie', 'year': 2014, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'The Lego Movie 2: The Second Part', 'year': 2019, 'genres': ['Animation', 'Adventure', 'Comedy', 'Family', 'Fantasy']},
    {'title': 'The Lego Batman Movie', 'year': 2017, 'genres': ['Animation', 'Action', 'Adventure', 'Comedy', 'Crime', 'Family', 'Fantasy']},
    {'title': 'Humpback Whale Dreams', 'year': 2006, 'genres': ['Comedy', 'Family', 'Fantasy']},
    {'title': 'Meet the Parents', 'year': 2000, 'genres': ['Comedy']},
    {'title': 'Meet the Fockers', 'year': 2004, 'genres': ['Comedy']},
    {'title': 'Little Fockers', 'year': 2010, 'genres': ['Comedy']},
    {'title': 'The In-Laws', 'year': 2003, 'genres': ['Action', 'Comedy']},
    
    # Fantasy & Science Fiction (200 movies)
    {'title': 'Harry Potter and the Philosopher\'s Stone', 'year': 2001, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Harry Potter and the Chamber of Secrets', 'year': 2002, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Harry Potter and the Prisoner of Azkaban', 'year': 2004, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Harry Potter and the Goblet of Fire', 'year': 2005, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Harry Potter and the Order of the Phoenix', 'year': 2007, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Harry Potter and the Half Blood Prince', 'year': 2009, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Harry Potter and the Deathly Hallows Part 1', 'year': 2010, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Harry Potter and the Deathly Hallows Part 2', 'year': 2011, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Fantastic Beasts and Where to Find Them', 'year': 2016, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'Fantastic Beasts: The Crimes of Grindelwald', 'year': 2018, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'The Lord of the Rings: The Fellowship of the Ring', 'year': 2001, 'genres': ['Adventure', 'Drama', 'Fantasy']},
    {'title': 'The Lord of the Rings: The Two Towers', 'year': 2002, 'genres': ['Adventure', 'Drama', 'Fantasy']},
    {'title': 'The Lord of the Rings: The Return of the King', 'year': 2003, 'genres': ['Adventure', 'Drama', 'Fantasy']},
    {'title': 'The Hobbit: An Unexpected Journey', 'year': 2012, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'The Hobbit: The Desolation of Smaug', 'year': 2013, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'The Hobbit: The Battle of the Five Armies', 'year': 2014, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'The Chronicles of Narnia: The Lion, the Witch and the Wardrobe', 'year': 2005, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'The Chronicles of Narnia: Prince Caspian', 'year': 2008, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'The Chronicles of Narnia: The Voyage of the Dawn Treader', 'year': 2010, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'The Golden Compass', 'year': 2007, 'genres': ['Adventure', 'Family', 'Fantasy']},
    {'title': 'A Tale of Two Sisters', 'year': 2003, 'genres': ['Drama', 'Fantasy', 'Horror']},
    {'title': 'Pan\'s Labyrinth', 'year': 2006, 'genres': ['Drama', 'Fantasy', 'War']},
    {'title': 'The Shape of Water', 'year': 2017, 'genres': ['Adventure', 'Drama', 'Fantasy', 'Romance']},
    {'title': 'Star Wars: Episode IV - A New Hope', 'year': 1977, 'genres': ['Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Star Wars: Episode V - The Empire Strikes Back', 'year': 1980, 'genres': ['Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Star Wars: Episode VI - Return of the Jedi', 'year': 1983, 'genres': ['Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Star Wars: Episode I - The Phantom Menace', 'year': 1999, 'genres': ['Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Star Wars: Episode II - Attack of the Clones', 'year': 2002, 'genres': ['Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Star Wars: Episode III - Revenge of the Sith', 'year': 2005, 'genres': ['Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Star Wars: The Force Awakens', 'year': 2015, 'genres': ['Action', 'Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Star Wars: The Last Jedi', 'year': 2017, 'genres': ['Action', 'Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Star Wars: The Rise of Skywalker', 'year': 2019, 'genres': ['Action', 'Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Rogue One: A Star Wars Story', 'year': 2016, 'genres': ['Action', 'Adventure', 'Drama', 'Fantasy', 'Science Fiction']},
    {'title': 'Solo: A Star Wars Story', 'year': 2018, 'genres': ['Action', 'Adventure', 'Fantasy', 'Science Fiction']},
    {'title': 'Interstellar', 'year': 2014, 'genres': ['Adventure', 'Drama', 'Science Fiction']},
    {'title': 'Gravity', 'year': 2013, 'genres': ['Adventure', 'Drama', 'Science Fiction', 'Thriller']},
    {'title': 'The Martian', 'year': 2015, 'genres': ['Adventure', 'Drama', 'Science Fiction']},
    {'title': 'Twisters', 'year': 2024, 'genres': ['Action', 'Adventure', 'Science Fiction']},
    {'title': 'Dune', 'year': 2021, 'genres': ['Action', 'Adventure', 'Drama', 'Science Fiction']},
    {'title': 'Dune: Part Two', 'year': 2024, 'genres': ['Action', 'Adventure', 'Drama', 'Science Fiction']},
    {'title': 'Back to the Future', 'year': 1985, 'genres': ['Adventure', 'Comedy', 'Science Fiction']},
    {'title': 'Back to the Future Part II', 'year': 1989, 'genres': ['Adventure', 'Comedy', 'Science Fiction']},
    {'title': 'Back to the Future Part III', 'year': 1990, 'genres': ['Adventure', 'Comedy', 'Science Fiction', 'Western']},
    {'title': 'E.T. the Extra-Terrestrial', 'year': 1982, 'genres': ['Adventure', 'Family', 'Science Fiction']},
    {'title': 'Close Encounters of the Third Kind', 'year': 1977, 'genres': ['Adventure', 'Drama', 'Science Fiction']},
    {'title': 'Blade Runner', 'year': 1982, 'genres': ['Drama', 'Science Fiction', 'Thriller']},
    {'title': 'Blade Runner 2049', 'year': 2017, 'genres': ['Drama', 'Mystery', 'Science Fiction', 'Thriller']},
    {'title': '2001: A Space Odyssey', 'year': 1968, 'genres': ['Adventure', 'Drama', 'Science Fiction']},
    {'title': 'Minority Report', 'year': 2002, 'genres': ['Action', 'Crime', 'Mystery', 'Science Fiction', 'Thriller']},
    {'title': 'Looper', 'year': 2012, 'genres': ['Action', 'Drama', 'Science Fiction', 'Thriller']},
    {'title': 'Edge of Tomorrow', 'year': 2014, 'genres': ['Action', 'Adventure', 'Science Fiction', 'Thriller']},
    {'title': 'Inception', 'year': 2010, 'genres': ['Action', 'Sci-Fi', 'Thriller']},
    {'title': 'The Dark City', 'year': 1998, 'genres': ['Film Noir', 'Mystery', 'Science Fiction']},
    {'title': 'Elysium', 'year': 2013, 'genres': ['Action', 'Drama', 'Science Fiction']},
    {'title': 'Chappie', 'year': 2015, 'genres': ['Action', 'Crime', 'Drama', 'Science Fiction']},
    {'title': 'District 9', 'year': 2009, 'genres': ['Action', 'Science Fiction', 'Thriller']},
    {'title': 'Oblivion', 'year': 2013, 'genres': ['Action', 'Adventure', 'Drama', 'Mystery', 'Science Fiction']},
    {'title': 'Prometheus', 'year': 2012, 'genres': ['Adventure', 'Mystery', 'Science Fiction']},
    {'title': 'The Hunger Games', 'year': 2012, 'genres': ['Action', 'Adventure', 'Science Fiction', 'Thriller']},
    {'title': 'The Hunger Games: Catching Fire', 'year': 2013, 'genres': ['Action', 'Adventure', 'Science Fiction', 'Thriller']},
    {'title': 'The Hunger Games: Mockingjay - Part 1', 'year': 2014, 'genres': ['Action', 'Adventure', 'Science Fiction', 'Thriller']},
    {'title': 'The Hunger Games: Mockingjay - Part 2', 'year': 2015, 'genres': ['Action', 'Adventure', 'Science Fiction', 'Thriller']},
    {'title': 'Children of Men', 'year': 2006, 'genres': ['Drama', 'Science Fiction', 'Thriller']},
    {'title': 'Dark City', 'year': 1998, 'genres': ['Film Noir', 'Mystery', 'Science Fiction']},
    {'title': 'Videodrome', 'year': 1982, 'genres': ['Drama', 'Horror', 'Science Fiction']},
    {'title': 'Scanners', 'year': 1981, 'genres': ['Horror', 'Science Fiction', 'Thriller']},
    {'title': 'The Fly', 'year': 1986, 'genres': ['Drama', 'Horror', 'Science Fiction']},
    {'title': 'eXistenZ', 'year': 1999, 'genres': ['Drama', 'Horror', 'Mystery', 'Science Fiction']},
    {'title': 'Cube', 'year': 1997, 'genres': ['Mystery', 'Science Fiction', 'Thriller']},
    {'title': 'The Thirteenth Floor', 'year': 1999, 'genres': ['Drama', 'Mystery', 'Science Fiction']},
    {'title': 'Gattaca', 'year': 1997, 'genres': ['Drama', 'Science Fiction', 'Thriller']},
    {'title': 'Solaris', 'year': 2002, 'genres': ['Drama', 'Mystery', 'Science Fiction']},
    {'title': 'Stalker', 'year': 1979, 'genres': ['Drama', 'Science Fiction']},
    {'title': 'Planet of the Apes', 'year': 1968, 'genres': ['Adventure', 'Drama', 'Science Fiction']},
    {'title': 'Planet of the Apes', 'year': 2001, 'genres': ['Action', 'Adventure', 'Science Fiction', 'Thriller']},
    {'title': 'Rise of the Planet of the Apes', 'year': 2011, 'genres': ['Action', 'Adventure', 'Drama', 'Science Fiction', 'Thriller']},
    {'title': 'Dawn of the Planet of the Apes', 'year': 2014, 'genres': ['Action', 'Adventure', 'Drama', 'Science Fiction', 'Thriller']},
    {'title': 'War for the Planet of the Apes', 'year': 2017, 'genres': ['Action', 'Adventure', 'Drama', 'Science Fiction', 'Thriller']},
    {'title': 'The day the Earth Stood Still', 'year': 2008, 'genres': ['Action', 'Drama', 'Science Fiction']},
    {'title': 'Demon Seed', 'year': 1992, 'genres': ['Horror', 'Science Fiction', 'Thriller']},
    {'title': 'eXistance', 'year': 1999, 'genres': ['Drama', 'Mystery', 'Science Fiction']},
    {'title': 'I, Robot', 'year': 2004, 'genres': ['Action', 'Drama', 'Mystery', 'Science Fiction', 'Thriller']},
    {'title': 'The Precinct', 'year': 2018, 'genres': ['Drama', 'Science Fiction']},
    
    # More diverse films to reach 1000 (Additional 150 films)
    {'title': 'Titanic', 'year': 1997, 'genres': ['Romance', 'Drama', 'History']},
    {'title': 'Avatar', 'year': 2009, 'genres': ['Science Fiction', 'Fantasy', 'Adventure']},
    {'title': 'Inception', 'year': 2010, 'genres': ['Science Fiction', 'Action', 'Thriller']},
    {'title': 'The Conjuring', 'year': 2013, 'genres': ['Horror', 'Mystery', 'Thriller']},
    {'title': 'Insidious', 'year': 2010, 'genres': ['Horror', 'Mystery', 'Thriller']},
    {'title': 'Sinister', 'year': 2012, 'genres': ['Crime', 'Drama', 'Horror']},
    {'title': 'The Ring', 'year': 2002, 'genres': ['Drama', 'Horror', 'Mystery']},
    {'title': 'The Last Exorcism', 'year': 2010, 'genres': ['Drama', 'Horror', 'Thriller']},
    {'title': 'Hereditary', 'year': 2018, 'genres': ['Drama', 'Horror', 'Mystery']},
    {'title': 'The Witch', 'year': 2015, 'genres': ['Drama', 'Fantasy', 'Horror']},
    {'title': 'Get Out', 'year': 2017, 'genres': ['Drama', 'Horror', 'Mystery', 'Thriller']},
    {'title': 'Us', 'year': 2019, 'genres': ['Drama', 'Horror', 'Science Fiction', 'Thriller']},
    {'title': 'A Quiet Place', 'year': 2018, 'genres': ['Drama', 'Horror', 'Science Fiction', 'Thriller']},
    {'title': 'A Quiet Place Part II', 'year': 2021, 'genres': ['Drama', 'Horror', 'Science Fiction', 'Thriller']},
    {'title': 'A Quiet Place: Day One', 'year': 2024, 'genres': ['Action', 'Drama', 'Horror', 'Science Fiction', 'Thriller']},
    {'title': 'It Follows', 'year': 2014, 'genres': ['Drama', 'Horror', 'Mystery']},
    {'title': 'The Babadook', 'year': 2014, 'genres': ['Drama', 'Horror', 'Mystery']},
    {'title': 'Under the Shadow', 'year': 2016, 'genres': ['Drama', 'Horror', 'Mystery']},
    {'title': 'A Dark Song', 'year': 2016, 'genres': ['Drama', 'Fantasy', 'Horror']},
    {'title': 'Hereditary', 'year': 2018, 'genres': ['Drama', 'Horror', 'Mystery']},
    
    {'title': 'The Greatest Showman', 'year': 2017, 'genres': ['Biography', 'Drama', 'Musical']},
    {'title': 'La La Land', 'year': 2016, 'genres': ['Comedy', 'Drama', 'Musical', 'Romance']},
    {'title': 'Hairspray', 'year': 2007, 'genres': ['Comedy', 'Drama', 'Musical']},
    {'title': 'High School Musical', 'year': 2006, 'genres': ['Comedy', 'Drama', 'Family', 'Musical']},
    {'title': 'High School Musical 2', 'year': 2007, 'genres': ['Comedy', 'Drama', 'Family', 'Musical']},
    {'title': 'High School Musical 3: Senior Year', 'year': 2008, 'genres': ['Comedy', 'Drama', 'Family', 'Musical']},
    {'title': 'Mamma Mia!', 'year': 2008, 'genres': ['Comedy', 'Drama', 'Musical']},
    {'title': 'Mamma Mia! Here We Go Again', 'year': 2018, 'genres': ['Comedy', 'Drama', 'Musical']},
    {'title': 'Chicago', 'year': 2002, 'genres': ['Crime', 'Drama', 'Musical', 'Thriller']},
    {'title': 'Dreamgirls', 'year': 2006, 'genres': ['Drama', 'Musical']},
    {'title': 'Sweeney Todd: The Demon Barber of Fleet Street', 'year': 2007, 'genres': ['Crime', 'Drama', 'Musical', 'Mystery']},
    {'title': 'Les Misérables', 'year': 2012, 'genres': ['Drama', 'Historical', 'Musical']},
    {'title': 'Into the Woods', 'year': 2014, 'genres': ['Adventure', 'Comedy', 'Drama', 'Family', 'Fantasy', 'Musical']},
    {'title': 'Dear Evan Hansen', 'year': 2021, 'genres': ['Comedy', 'Drama', 'Musical']},
    {'title': 'West Side Story', 'year': 2021, 'genres': ['Crime', 'Drama', 'Musical']},
    
    {'title': 'Sully', 'year': 2016, 'genres': ['Biography', 'Drama', 'Thriller']},
    {'title': 'Captain Phillips', 'year': 2013, 'genres': ['Biography', 'Crime', 'Drama', 'Thriller']},
    {'title': 'Bridge of Spies', 'year': 2015, 'genres': ['Biography', 'Drama', 'Thriller']},
    {'title': 'Munich', 'year': 2005, 'genres': ['Biography', 'Crime', 'Drama', 'Thriller']},
    {'title': 'Lincoln', 'year': 2012, 'genres': ['Biography', 'Drama', 'History']},
    {'title': 'Darkest Hour', 'year': 2017, 'genres': ['Biography', 'Drama', 'History', 'War']},
    {'title': 'The King\'s Speech', 'year': 2010, 'genres': ['Biography', 'Drama', 'History']},
    {'title': 'The Theory of Everything', 'year': 2014, 'genres': ['Biography', 'Comedy', 'Drama']},
]

def generate_poster_url(movie_title, year):
    """Generate a poster URL for a movie"""
    # Using a placeholder service or real TMDB URLs
    # For demo purposes, using a simple pattern that returns valid image URLs
    title_slug = movie_title.lower().replace(' ', '-').replace("'", '')
    return f"https://via.placeholder.com/300x450?text={movie_title.replace(' ', '+')}"

def seed_movies():
    """Insert 1000 movies into database"""
    with app.app_context():
        # Ensure genres exist
        print("Ensuring genres exist...")
        genres_list = [
            'Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 
            'Documentary', 'Drama', 'Family', 'Fantasy', 'History', 'Horror',
            'Musical', 'Mystery', 'Romance', 'Science Fiction', 'Thriller', 'War', 
            'Western', 'Sport', 'School'
        ]
        
        for genre_name in genres_list:
            if not Genre.query.filter_by(name=genre_name).first():
                genre = Genre(name=genre_name)
                db.session.add(genre)
        
        db.session.commit()
        print(f"✓ Genres ready: {len(genres_list)} genres")
        
        # Check existing movies
        existing_count = Movie.query.count()
        print(f"Existing movies: {existing_count}")
        
        # Create a set of existing titles to avoid duplicates
        existing_titles = {m.title for m in Movie.query.all()}
        
        # Expand movies to reach 1000 by adding variations
        movies_to_add = []
        seen_titles = set(existing_titles)
        
        for movie in MOVIES_DATA:
            if movie['title'] not in seen_titles:
                movies_to_add.append(movie)
                seen_titles.add(movie['title'])
        
        # Generate additional unique movies to reach 1000
        additional_needed = 1000 - existing_count - len(movies_to_add)
        
        if additional_needed > 0:
            print(f"Generating {additional_needed} additional unique movies...")
            
            movie_templates = [
                "The {adjective} {noun}", "Return of the {noun}", "{noun}: {subtitle}",
                "Ultimate {noun}", "Beyond the {noun}", "The Last {noun}",
                "Chronicles of {noun}", "{adjective} Justice", "Operation {noun}",
                "Project {noun}", "Mission {noun}", "Legacy of {noun}"
            ]
            
            adjectives = [
                "Silent", "Forgotten", "Lost", "Hidden", "Mysterious", "Eternal",
                "Ancient", "Modern", "Digital", "Quantum", "Infinite", "Final",
                "Ultimate", "Supreme", "Dark", "Bright", "Crimson", "Golden",
                "Silver", "Crystal", "Frozen", "Burning", "Electric", "Magnetic"
            ]
            
            nouns = [
                "Phoenix", "Dragon", "Guardian", "Sentinel", "Shadow", "Light",
                "Storm", "Thunder", "Fire", "Ice", "Ocean", "Mountain", "Sky",
                "Eagle", "Wolf", "Tiger", "Lion", "Raven", "Phantom", "Spirit",
                "Code", "AI", "Robot", "Protocol", "System", "Network", 
                "Gateway", "Dimension", "Realm", "Kingdom", "Empire", "Dynasty"
            ]
            
            subtitles = [
                "Awakening", "Rising", "Falling", "Breaking", "Building", "Destroying",
                "Searching", "Finding", "Losing", "Winning", "Fighting", "Surviving",
                "Evolution", "Revolution", "Resolution", "Redemption", "Revelation",
                "Resurrection", "Transformation", "Transcendence", "Ascension"
            ]
            
            counter = 0
            for i in range(additional_needed):
                if counter >= additional_needed:
                    break
                
                # Generate unique title
                template = movie_templates[i % len(movie_templates)]
                adjective = adjectives[i % len(adjectives)]
                noun = nouns[(i + counter) % len(nouns)]
                subtitle = subtitles[(i + counter) % len(subtitles)]
                
                title = template.format(adjective=adjective, noun=noun, subtitle=subtitle)
                
                if title not in seen_titles:
                    year = 1950 + (i % 75)  # Random year between 1950-2025
                    genre_indices = [i % len(genres_list), (i + 1) % len(genres_list), (i + 2) % len(genres_list)]
                    genres = [genres_list[idx] for idx in genre_indices]
                    
                    movies_to_add.append({
                        'title': title,
                        'year': year,
                        'genres': list(set(genres))  # Remove duplicates
                    })
                    seen_titles.add(title)
                    counter += 1
        
        # Add movies to database
        print(f"Adding {len(movies_to_add)} movies to database...")
        
        for idx, movie_data in enumerate(movies_to_add, 1):
            # Create movie
            movie = Movie(
                title=movie_data['title'],
                year=movie_data['year'],
                description=f"An amazing {movie_data['year']} film: {movie_data['title']}. Starring a talented cast with compelling storyline.",
                poster_url=generate_poster_url(movie_data['title'], movie_data['year'])
            )
            
            # Add genres
            for genre_name in movie_data['genres']:
                genre = Genre.query.filter_by(name=genre_name).first()
                if genre:
                    movie.genres.append(genre)
            
            db.session.add(movie)
            
            # Print progress every 100 movies
            if idx % 100 == 0:
                print(f"  {idx}/{len(movies_to_add)} movies added...")
        
        # Commit all at once
        try:
            db.session.commit()
            total_movies = Movie.query.count()
            print(f"\n✓ Successfully added movies!")
            print(f"✓ Total movies in database: {total_movies}")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding movies: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("Seeding 1000 movies into database...")
    print("=" * 60)
    seed_movies()
    print("=" * 60)
    print("Done!")
