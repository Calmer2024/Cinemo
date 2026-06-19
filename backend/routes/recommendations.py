"""推荐系统路由：ALS协同过滤 + 内容回退 + 相似推荐 + 数据看板"""
from flask import Blueprint, request, jsonify

from models import db, Movie, Rating, Recommendation
from routes.auth import token_required

recommendations_bp = Blueprint('recommendations', __name__, url_prefix='/api/recommendations')


def _wrap_rec(movie_id, score, movie):
    """将推荐结果统一包装为前端期望的格式"""
    return {
        'movie_id': movie_id,
        'score': score,
        'movie': movie.to_dict() if movie else None,
    }


@recommendations_bp.route('', methods=['GET'])
@token_required
def get_recommendations(current_user):
    """获取当前用户的推荐列表（ALS结果优先，否则用热门/相似回退）"""
    algorithm = request.args.get('algorithm', 'als')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)

    # 1. 先查 ALS 推荐结果
    pagination = Recommendation.query.filter_by(
        user_id=current_user.id,
        algorithm=algorithm
    ).order_by(Recommendation.score.desc())\
     .paginate(page=page, per_page=per_page, error_out=False)

    if pagination.total > 0:
        recs = []
        for r in pagination.items:
            recs.append(_wrap_rec(r.movie_id, r.score, r.movie))
        return jsonify({
            'recommendations': recs,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'method': 'als',
        })

    # 2. 回退：基于用户评分过的类型推荐相似高分电影
    from sqlalchemy import or_
    user_ratings = Rating.query.filter_by(user_id=current_user.id).all()
    rated_movie_ids = {r.movie_id for r in user_ratings}

    if user_ratings:
        liked_genres = set()
        for r in user_ratings:
            if r.score >= 3.5:
                movie = Movie.query.get(r.movie_id)
                if movie and movie.genres:
                    for g in movie.genres.split('|'):
                        liked_genres.add(g.strip())

        if liked_genres:
            conditions = [Movie.genres.ilike(f'%{g}%') for g in liked_genres]
            candidates = Movie.query.filter(
                or_(*conditions),
                ~Movie.id.in_(rated_movie_ids)
            ).order_by(Movie.avg_rating.desc()).limit(per_page).all()

            if candidates:
                recs = []
                for m in candidates:
                    recs.append(_wrap_rec(m.id, m.avg_rating or 3.0, m))
                return jsonify({
                    'recommendations': recs,
                    'total': len(candidates),
                    'page': 1,
                    'per_page': per_page,
                    'method': 'content_based',
                })

    # 3. 最终回退：返回高分热门电影
    hot_movies = Movie.query.filter(
        ~Movie.id.in_(rated_movie_ids) if rated_movie_ids else True
    ).filter(
        Movie.avg_rating > 0
    ).order_by(Movie.avg_rating.desc(), Movie.rating_count.desc())\
     .limit(per_page).all()

    if not hot_movies:
        hot_movies = Movie.query.order_by(Movie.id.desc()).limit(per_page).all()

    recs = [_wrap_rec(m.id, m.avg_rating or 3.0, m) for m in hot_movies]
    return jsonify({
        'recommendations': recs,
        'total': len(hot_movies),
        'page': 1,
        'per_page': per_page,
        'method': 'popular',
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

    return jsonify({
        'similar': [m.to_dict() for m in similar]
    })


@recommendations_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """数据看板统计"""
    from sqlalchemy import func

    total_movies = Movie.query.count()
    total_ratings = Rating.query.count()
    total_users = db.session.query(func.count(func.distinct(Rating.user_id))).scalar()

    rating_dist = db.session.query(
        func.floor(Rating.score).label('score'),
        func.count().label('count')
    ).group_by(func.floor(Rating.score)).all()

    genre_counts = {}
    movies = Movie.query.all()
    for m in movies:
        if m.genres:
            for g in m.genres.split('|'):
                g = g.strip()
                genre_counts[g] = genre_counts.get(g, 0) + 1
    genre_top = sorted(genre_counts.items(), key=lambda x: -x[1])[:10]

    hot_movies = Movie.query.filter(Movie.rating_count > 0)\
        .order_by(Movie.avg_rating.desc(), Movie.rating_count.desc())\
        .limit(10).all()

    recent_ratings = Rating.query.order_by(Rating.created_at.desc()).limit(10).all()

    return jsonify({
        'total_movies': total_movies,
        'total_ratings': total_ratings,
        'total_users': total_users,
        'rating_distribution': [{'score': int(s), 'count': c} for s, c in rating_dist],
        'genre_distribution': [{'genre': g, 'count': c} for g, c in genre_top],
        'hot_movies': [m.to_dict() for m in hot_movies],
        'recent_ratings': [r.to_dict() for r in recent_ratings],
    })


@recommendations_bp.route('/trigger', methods=['POST'])
@token_required
def trigger_recommendation(current_user):
    """手动触发 Spark 推荐计算"""
    import subprocess
    import sys

    try:
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
