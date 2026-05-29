from flask import Flask
from flask_cors import CORS

from config import Config
from models import db

from routes.auth import auth_bp
from routes.movies import movies_bp
from routes.ratings import ratings_bp
from routes.recommendations import recommendations_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化扩展
    db.init_app(app)
    CORS(app)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(ratings_bp)
    app.register_blueprint(recommendations_bp)

    # 健康检查
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Movie Recommender API is running'}

    # 首次运行时自动建表
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
