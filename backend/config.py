import os

class Config:
    # GaussDB 连接配置 (兼容 PostgreSQL 协议)
    # 格式: postgresql://用户名:密码@主机:端口/数据库名
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://gaussdb:gaussdb123@localhost:5433/movie_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Spark 配置
    SPARK_MASTER = os.environ.get('SPARK_MASTER', 'local[*]')

    # 分页默认值
    DEFAULT_PAGE_SIZE = 12
