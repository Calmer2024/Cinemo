"""
Simplified seed script - uses INSERT only, no DELETE.
"""
import random
from app import create_app
from models import db, User, Movie, Rating

MOVIES = [
    {"title": "The Shawshank Redemption", "genres": "Drama|Crime", "director": "Frank Darabont", "actors": "Tim Robbins|Morgan Freeman", "year": 1994, "description": "Two imprisoned men bond over a number of years."},
    {"title": "The Godfather", "genres": "Drama|Crime", "director": "Francis Ford Coppola", "actors": "Marlon Brando|Al Pacino", "year": 1972, "description": "The aging patriarch transfers control to his son."},
    {"title": "The Dark Knight", "genres": "Action|Crime|Drama", "director": "Christopher Nolan", "actors": "Christian Bale|Heath Ledger", "year": 2008, "description": "Batman faces his greatest test against the Joker."},
    {"title": "Pulp Fiction", "genres": "Crime|Drama", "director": "Quentin Tarantino", "actors": "John Travolta|Uma Thurman", "year": 1994, "description": "Lives of mob hitmen and a boxer intertwine."},
    {"title": "Forrest Gump", "genres": "Drama|Romance", "director": "Robert Zemeckis", "actors": "Tom Hanks|Robin Wright", "year": 1994, "description": "An Alabama man witnesses history."},
    {"title": "Inception", "genres": "Action|Sci-Fi|Thriller", "director": "Christopher Nolan", "actors": "Leonardo DiCaprio|Joseph Gordon-Levitt", "year": 2010, "description": "A thief steals secrets through dream technology."},
    {"title": "Fight Club", "genres": "Drama", "director": "David Fincher", "actors": "Brad Pitt|Edward Norton", "year": 1999, "description": "An underground fight club is formed."},
    {"title": "The Matrix", "genres": "Action|Sci-Fi", "director": "Lana Wachowski|Lilly Wachowski", "actors": "Keanu Reeves|Laurence Fishburne", "year": 1999, "description": "A hacker learns the truth about reality."},
    {"title": "Interstellar", "genres": "Adventure|Drama|Sci-Fi", "director": "Christopher Nolan", "actors": "Matthew McConaughey|Anne Hathaway", "year": 2014, "description": "Explorers travel through a wormhole."},
    {"title": "Parasite", "genres": "Comedy|Drama|Thriller", "director": "Bong Joon Ho", "actors": "Kang-ho Song|Sun-kyun Lee", "year": 2019, "description": "Class discrimination threatens two families."},
    {"title": "Spirited Away", "genres": "Animation|Adventure|Family", "director": "Hayao Miyazaki", "actors": "Rumi Hiiragi|Miyu Irino", "year": 2001, "description": "A girl enters the world of spirits."},
    {"title": "Schindler's List", "genres": "Biography|Drama|History", "director": "Steven Spielberg", "actors": "Liam Neeson|Ralph Fiennes", "year": 1993, "description": "A German saves his Jewish workers during WWII."},
    {"title": "Titanic", "genres": "Drama|Romance", "director": "James Cameron", "actors": "Leonardo DiCaprio|Kate Winslet", "year": 1997, "description": "Love story on the ill-fated ship."},
    {"title": "Whiplash", "genres": "Drama|Music", "director": "Damien Chazelle", "actors": "Miles Teller|J.K. Simmons", "year": 2014, "description": "A drummer at a music conservatory."},
    {"title": "La La Land", "genres": "Comedy|Drama|Musical", "director": "Damien Chazelle", "actors": "Ryan Gosling|Emma Stone", "year": 2016, "description": "A pianist and actress fall in love."},
    {"title": "The Lion King", "genres": "Animation|Adventure|Drama", "director": "Roger Allers|Rob Minkoff", "actors": "Matthew Broderick|Jeremy Irons", "year": 1994, "description": "Lion prince flees his kingdom."},
    {"title": "Gladiator", "genres": "Action|Adventure|Drama", "director": "Ridley Scott", "actors": "Russell Crowe|Joaquin Phoenix", "year": 2000, "description": "A former Roman General seeks vengeance."},
    {"title": "Avengers: Endgame", "genres": "Action|Adventure|Drama", "director": "Anthony Russo|Joe Russo", "actors": "Robert Downey Jr.|Chris Evans", "year": 2019, "description": "Avengers assemble to undo Thanos."},
    {"title": "The Prestige", "genres": "Drama|Mystery|Sci-Fi", "director": "Christopher Nolan", "actors": "Christian Bale|Hugh Jackman", "year": 2006, "description": "Two magicians in bitter rivalry."},
    {"title": "Up", "genres": "Animation|Adventure|Comedy", "director": "Pete Docter|Bob Peterson", "actors": "Edward Asner|Jordan Nagai", "year": 2009, "description": "Old man flies house to South America."},
]

TEST_USERS = [
    {"username": "alice", "email": "alice@example.com", "password": "123456"},
    {"username": "bob", "email": "bob@example.com", "password": "123456"},
    {"username": "charlie", "email": "charlie@example.com", "password": "123456"},
    {"username": "diana", "email": "diana@example.com", "password": "123456"},
    {"username": "eve", "email": "eve@example.com", "password": "123456"},
]


def seed():
    app = create_app()
    with app.app_context():
        # Check if already seeded
        if Movie.query.count() > 0:
            print(f"Already has {Movie.query.count()} movies, skipping seed")
            return

        # Create users
        users = []
        for u in TEST_USERS:
            existing = User.query.filter_by(username=u['username']).first()
            if existing:
                users.append(existing)
                continue
            user = User(username=u['username'], email=u['email'])
            user.set_password(u['password'])
            db.session.add(user)
            users.append(user)
        db.session.commit()
        print(f"Created {len(users)} users")

        # Create movies
        movies = []
        for m in MOVIES:
            movie = Movie(**m)
            db.session.add(movie)
            movies.append(movie)
        db.session.commit()
        print(f"Created {len(movies)} movies")

        # Simulate ratings
        rating_count = 0
        for user in users:
            num_ratings = random.randint(8, min(15, len(movies)))
            rated_movies = random.sample(movies, num_ratings)
            for movie in rated_movies:
                score = round(random.uniform(2.5, 5.0) * 2) / 2
                score = max(1.0, min(5.0, score))
                try:
                    rating = Rating(user_id=user.id, movie_id=movie.id, score=score)
                    db.session.add(rating)
                    rating_count += 1
                except Exception:
                    db.session.rollback()
        db.session.commit()
        print(f"Created {rating_count} ratings")
        print("Seed complete!")


if __name__ == '__main__':
    seed()
