from flask import Blueprint, request, jsonify

from models import db, Rating, Movie
from routes.auth import token_required

ratings_bp = Blueprint('ratings', __name__, url_prefix='/api/ratings')


@ratings_bp.route('', methods=['POST'])
@token_required
def create_rating(current_user):
    """提交评分"""
    data = request.get_json()
    movie_id = data.get('movie_id')
    score = data.get('score')
    review = data.get('review', '').strip()

    if not movie_id or not score:
        return jsonify({'error': '电影ID和评分不能为空'}), 400

    if not (1 <= score <= 5):
        return jsonify({'error': '评分范围为 1-5'}), 400

    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'error': '电影不存在'}), 404

    # 检查是否已评分，已评分则更新
    existing = Rating.query.filter_by(user_id=current_user.id, movie_id=movie_id).first()
    if existing:
        old_score = existing.score
        existing.score = score
        existing.review = review
        # 重新计算平均分
        movie.avg_rating = (movie.avg_rating * movie.rating_count - old_score + score) / movie.rating_count
    else:
        rating = Rating(
            user_id=current_user.id,
            movie_id=movie_id,
            score=score,
            review=review
        )
        db.session.add(rating)
        # 更新电影平均分
        total = movie.avg_rating * movie.rating_count + score
        movie.rating_count += 1
        movie.avg_rating = total / movie.rating_count

    db.session.commit()
    return jsonify({'message': '评分成功', 'movie': movie.to_dict()}), 201


@ratings_bp.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie_ratings(movie_id):
    """获取某部电影的所有评分"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    pagination = Rating.query.filter_by(movie_id=movie_id)\
        .order_by(Rating.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'ratings': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })


@ratings_bp.route('/user', methods=['GET'])
@token_required
def get_user_ratings(current_user):
    """获取当前用户的所有评分"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Rating.query.filter_by(user_id=current_user.id)\
        .order_by(Rating.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'ratings': [r.to_dict() for r in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })


@ratings_bp.route('/<int:rating_id>', methods=['DELETE'])
@token_required
def delete_rating(current_user, rating_id):
    """删除评分"""
    rating = Rating.query.get_or_404(rating_id)
    if rating.user_id != current_user.id:
        return jsonify({'error': '无权删除'}), 403

    movie = Movie.query.get(rating.movie_id)
    if movie:
        if movie.rating_count > 1:
            movie.avg_rating = (movie.avg_rating * movie.rating_count - rating.score) / (movie.rating_count - 1)
        else:
            movie.avg_rating = 0
        movie.rating_count -= 1

    db.session.delete(rating)
    db.session.commit()
    return jsonify({'message': '删除成功'})
