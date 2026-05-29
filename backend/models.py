from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar = db.Column(db.String(256), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ratings = db.relationship('Rating', backref='user', lazy='dynamic')
    recommendations = db.relationship('Recommendation', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar': self.avatar,
            'created_at': self.created_at.isoformat()
        }


class Movie(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    genres = db.Column(db.String(200), default='')       # 用 | 分隔，如 "Action|Comedy"
    director = db.Column(db.String(100), default='')
    actors = db.Column(db.String(300), default='')
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(500), default='')
    description = db.Column(db.Text, default='')
    avg_rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)

    ratings = db.relationship('Rating', backref='movie', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'genres': self.genres.split('|') if self.genres else [],
            'director': self.director,
            'actors': self.actors,
            'year': self.year,
            'poster_url': self.poster_url,
            'description': self.description,
            'avg_rating': round(self.avg_rating, 1),
            'rating_count': self.rating_count
        }


class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 1-5 分
    review = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'movie_id', name='uq_user_movie'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'score': self.score,
            'review': self.review,
            'created_at': self.created_at.isoformat(),
            'username': self.user.username if self.user else None
        }


class Recommendation(db.Model):
    __tablename__ = 'recommendations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 预测评分
    algorithm = db.Column(db.String(50), default='als')  # als, content_based
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movie = db.relationship('Movie', backref='recommended_to')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'movie_id': self.movie_id,
            'movie': self.movie.to_dict() if self.movie else None,
            'score': round(self.score, 2),
            'algorithm': self.algorithm,
            'created_at': self.created_at.isoformat()
        }
