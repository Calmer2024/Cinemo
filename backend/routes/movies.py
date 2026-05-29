from flask import Blueprint, request, jsonify
from sqlalchemy import or_

from models import db, Movie
from routes.auth import token_required

movies_bp = Blueprint('movies', __name__, url_prefix='/api/movies')


@movies_bp.route('', methods=['GET'])
def list_movies():
    """电影列表 - 支持搜索、分类筛选、分页"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    search = request.args.get('search', '').strip()
    genre = request.args.get('genre', '').strip()
    sort_by = request.args.get('sort_by', 'rating')  # rating, year, title

    query = Movie.query

    # 搜索
    if search:
        query = query.filter(
            or_(
                Movie.title.ilike(f'%{search}%'),
                Movie.director.ilike(f'%{search}%'),
                Movie.actors.ilike(f'%{search}%')
            )
        )

    # 类型筛选
    if genre:
        query = query.filter(Movie.genres.ilike(f'%{genre}%'))

    # 排序
    if sort_by == 'year':
        query = query.order_by(Movie.year.desc())
    elif sort_by == 'title':
        query = query.order_by(Movie.title)
    else:  # rating
        query = query.order_by(Movie.avg_rating.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'movies': [m.to_dict() for m in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@movies_bp.route('/genres', methods=['GET'])
def list_genres():
    """获取所有电影类型"""
    movies = Movie.query.all()
    genre_set = set()
    for m in movies:
        if m.genres:
            for g in m.genres.split('|'):
                genre_set.add(g.strip())
    return jsonify({'genres': sorted(genre_set)})


@movies_bp.route('/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """获取电影详情"""
    movie = Movie.query.get_or_404(movie_id)
    return jsonify({'movie': movie.to_dict()})


@movies_bp.route('', methods=['POST'])
@token_required
def create_movie(current_user):
    """添加电影（管理员用）"""
    data = request.get_json()
    movie = Movie(
        title=data['title'],
        genres='|'.join(data.get('genres', [])),
        director=data.get('director', ''),
        actors=data.get('actors', ''),
        year=data.get('year'),
        poster_url=data.get('poster_url', ''),
        description=data.get('description', '')
    )
    db.session.add(movie)
    db.session.commit()
    return jsonify({'movie': movie.to_dict()}), 201


@movies_bp.route('/<int:movie_id>', methods=['PUT'])
@token_required
def update_movie(current_user, movie_id):
    """更新电影信息"""
    movie = Movie.query.get_or_404(movie_id)
    data = request.get_json()

    if 'title' in data:
        movie.title = data['title']
    if 'genres' in data:
        movie.genres = '|'.join(data['genres'])
    if 'director' in data:
        movie.director = data['director']
    if 'actors' in data:
        movie.actors = data['actors']
    if 'year' in data:
        movie.year = data['year']
    if 'poster_url' in data:
        movie.poster_url = data['poster_url']
    if 'description' in data:
        movie.description = data['description']

    db.session.commit()
    return jsonify({'movie': movie.to_dict()})


@movies_bp.route('/<int:movie_id>', methods=['DELETE'])
@token_required
def delete_movie(current_user, movie_id):
    """删除电影"""
    movie = Movie.query.get_or_404(movie_id)
    db.session.delete(movie)
    db.session.commit()
    return jsonify({'message': '删除成功'})
