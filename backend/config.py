import os
from urllib.parse import quote_plus


class Config:
    # GaussDB 连接配置 (兼容 PostgreSQL 协议)
    # 优先使用 DATABASE_URL，否则从独立环境变量构建
    DATABASE_URL = os.environ.get('DATABASE_URL', '')

    if not DATABASE_URL:
        DB_HOST = os.environ.get('DB_HOST', 'localhost')
        DB_PORT = os.environ.get('DB_PORT', '5432')
        DB_USER = os.environ.get('DB_USER', 'gaussadmin')
        DB_PASSWORD = os.environ.get('DB_PASSWORD', 'GaussDB@2024')
        DB_NAME = os.environ.get('DB_NAME', 'movie_db')
        # URL-encode password to handle special characters like @
        encoded_password = quote_plus(DB_PASSWORD)
        SQLALCHEMY_DATABASE_URI = (
            f'postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        )
    else:
        SQLALCHEMY_DATABASE_URI = DATABASE_URL

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 强制 UTF8 编码以支持中文字符（GaussDB 默认 SQL_ASCII）
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'client_encoding': 'UTF8'}
    }

    # JWT 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Spark 配置
    SPARK_MASTER = os.environ.get('SPARK_MASTER', 'local[*]')

    # 分页默认值
    DEFAULT_PAGE_SIZE = 12
