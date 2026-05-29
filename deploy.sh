#!/bin/bash
# 华为云部署脚本 (轻量化配置)

echo "=========================================="
echo "  电影推荐系统 - 华为云部署脚本"
echo "=========================================="

# 1. 检查 Docker
echo "[1/7] 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi
echo "  Docker 已安装"

# 2. 停止旧容器
echo "[2/7] 停止旧容器..."
docker-compose -f docker-compose.prod.yml down 2>/dev/null
docker rm -f gaussdb 2>/dev/null

# 3. 启动 GaussDB (轻量化)
echo "[3/7] 启动 GaussDB (内存限制 2GB)..."
docker-compose -f docker-compose.prod.yml up -d gaussdb

# 4. 等待 GaussDB 启动
echo "[4/7] 等待 GaussDB 启动 (约60秒)..."
for i in {1..60}; do
    if docker exec gaussdb pg_isready -U gaussdb -d movie_db &>/dev/null; then
        echo "  GaussDB 已就绪!"
        break
    fi
    if [ $i -eq 60 ]; then
        echo "  超时，请检查日志: docker logs gaussdb"
        exit 1
    fi
    sleep 2
done

# 5. 创建数据库表
echo "[5/7] 创建数据库表..."
docker exec gaussdb psql -U gaussdb -d movie_db -c "
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    avatar VARCHAR(256) DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS movies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    genres VARCHAR(200) DEFAULT '',
    director VARCHAR(100) DEFAULT '',
    actors VARCHAR(300) DEFAULT '',
    year INTEGER,
    poster_url VARCHAR(500) DEFAULT '',
    description TEXT DEFAULT '',
    avg_rating FLOAT DEFAULT 0.0,
    rating_count INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    movie_id INTEGER REFERENCES movies(id) NOT NULL,
    score FLOAT NOT NULL,
    review TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, movie_id)
);
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    movie_id INTEGER REFERENCES movies(id) NOT NULL,
    score FLOAT NOT NULL,
    algorithm VARCHAR(50) DEFAULT 'als',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"
echo "  数据库表创建完成"

# 6. 构建并启动后端和前端
echo "[6/7] 构建并启动后端和前端..."
docker-compose -f docker-compose.prod.yml up -d --build backend frontend

echo "[7/7] 等待服务启动..."
sleep 30

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "访问地址: http://$(curl -s ifconfig.me)"
echo ""
echo "测试账号: alice / 123456"
echo ""
echo "查看状态: docker-compose -f docker-compose.prod.yml ps"
echo "查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo ""
