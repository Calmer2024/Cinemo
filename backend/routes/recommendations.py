import subprocess
import sys

from flask import Blueprint, request, jsonify

from models import db, Movie, Rating, Recommendation
from routes.auth import token_required

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')


@recommendations_bp.route('', methods=['GET'])
@token_required
def get_recommendations(current_user):
    """获取当前用户的推荐列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    algorithm = request.args.get('algorithm', 'als')

    pagination = Recommendation.query.filter_by(
        user_id=current_user.id,
        algorithm=algorithm
    ).order_by(Recommendation.score.desc())\
     .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'recommendations': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })


@recommendations_bp.route('/similar/<int:movie_id>', methods=['GET'])
def get_similar_movies(movie_id):
    """获取相似电影推荐（基于类型）"""
    movie = Movie.query.get_or_404(movie_id)
    if not movie.genres:
        return jsonify({'similar': []})

    genres = movie.genres.split('|')
    conditions = [Movie.genres.ilike(f'%{g}%') for g in genres]

    from sqlalchemy import or_
    similar = Movie.query.filter(
        or_(*conditions),
        Movie.id != movie_id
    ).order_by(Movie.avg_rating.desc()).limit(6).all()

    return jsonify({'similar': [m.to_dict() for m in similar]})


@recommendations_bp.route('/trigger', methods=['POST'])
@token_required
def trigger_recommendation(current_user):
    """手动触发 Spark 推荐计算"""
    try:
        # 调用 Spark 推荐脚本
        result = subprocess.run(
            [sys.executable, 'spark_jobs/recommend.py'],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            return jsonify({'message': '推荐计算完成', 'output': result.stdout})
        else:
            return jsonify({'error': '推荐计算失败', 'detail': result.stderr}), 500
    except subprocess.TimeoutExpired:
        return jsonify({'error': '推荐计算超时'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@recommendations_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """数据看板统计"""
    from sqlalchemy import func

    # 总数统计
    total_movies = Movie.query.count()
    total_ratings = Rating.query.count()
    total_users = db.session.query(func.count(db.distinct(Rating.user_id))).scalar()

    # 评分分布
    rating_dist = db.session.query(
        func.floor(Rating.score).label('score'),
        func.count().label('count')
    ).group_by(func.floor(Rating.score)).all()

    # 类型分布 (top 10)
    genre_counts = {}
    movies = Movie.query.all()
    for m in movies:
        if m.genres:
            for g in m.genres.split('|'):
                g = g.strip()
                genre_counts[g] = genre_counts.get(g, 0) + 1
    genre_top = sorted(genre_counts.items(), key=lambda x: -x[1])[:10]

    # 热门电影 top 10
    hot_movies = Movie.query.filter(Movie.rating_count > 0)\
        .order_by(Movie.avg_rating.desc(), Movie.rating_count.desc())\
        .limit(10).all()

    # 最新评分
    recent_ratings = Rating.query.order_by(Rating.created_at.desc()).limit(10).all()

    return jsonify({
        'total_movies': total_movies,
        'total_ratings': total_ratings,
        'total_users': total_users,
        'rating_distribution': [{'score': int(s), 'count': c} for s, c in rating_dist],
        'genre_distribution': [{'genre': g, 'count': c} for g, c in genre_top],
        'hot_movies': [m.to_dict() for m in hot_movies],
        'recent_ratings': [r.to_dict() for r in recent_ratings]
    })
