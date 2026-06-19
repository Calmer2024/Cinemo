from app import create_app
from models import db, Movie
from poster_map import POSTER_PATH_BY_TITLE


def sync_posters():
    app = create_app()
    with app.app_context():
        updated = 0
        matched_titles = set()

        for movie in Movie.query.all():
            poster_url = POSTER_PATH_BY_TITLE.get(movie.title)
            if not poster_url:
                continue

            matched_titles.add(movie.title)
            if movie.poster_url != poster_url:
                movie.poster_url = poster_url
                updated += 1

        if updated:
            db.session.commit()

        missing_movies = sorted(set(POSTER_PATH_BY_TITLE) - matched_titles)
        print(f"Posters updated: {updated}")
        if missing_movies:
            print(f"Movies not found: {', '.join(missing_movies)}")


if __name__ == "__main__":
    sync_posters()
