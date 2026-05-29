from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Blueprint, request, jsonify, current_app

from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def token_required(f):
    """JWT 认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'error': '缺少认证令牌'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': '用户不存在'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': '令牌已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': '无效令牌'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


def generate_token(user_id):
    return jwt.encode(
        {'user_id': user_id, 'exp': datetime.utcnow() + timedelta(days=7)},
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据为空'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': '用户名、邮箱和密码不能为空'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': '用户名已存在'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': '邮箱已注册'}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        'message': '注册成功',
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据为空'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error': '用户名或密码错误'}), 401

    token = generate_token(user.id)
    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': user.to_dict()
    })


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_me(current_user):
    return jsonify({'user': current_user.to_dict()})


@auth_bp.route('/me', methods=['PUT'])
@token_required
def update_me(current_user):
    data = request.get_json()
    if data.get('email'):
        current_user.email = data['email']
    if data.get('avatar'):
        current_user.avatar = data['avatar']
    db.session.commit()
    return jsonify({'user': current_user.to_dict()})
