import re
from flask import Flask
from flask_cors import CORS
from sqlalchemy.dialects.postgresql.base import PGDialect

from config import Config
from models import db

# Monkey-patch: 让 SQLAlchemy 兼容 openGauss 的版本号格式
# openGauss 返回的版本字符串类似: "(openGauss 5.0.0 build ) compiled at ..."
_original_get_server_version_info = PGDialect._get_server_version_info


def _patched_get_server_version_info(self, connection):
    from sqlalchemy import text
    cursor = connection.execute(
        text("SELECT version() AS server_version")
    )
    row = cursor.fetchone()
    if not row:
        raise AssertionError("Could not retrieve server version info")
    version_str = row[0]
    # Try standard PostgreSQL format first
    match = re.search(
        r"(\d+)\.(\d+)(?:\.(\d+))?", version_str
    )
    if match:
        return tuple(int(x) for x in match.group(1, 2, 3) if x is not None)
    raise AssertionError(
        f"Could not determine version from string {version_str!r}"
    )


PGDialect._get_server_version_info = _patched_get_server_version_info

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
