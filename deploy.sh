#!/bin/bash
# 华为云部署脚本 (轻量化配置)

set -euo pipefail

echo "=========================================="
echo "  电影推荐系统 - 华为云部署脚本"
echo "=========================================="

COMPOSE="docker compose"
if ! $COMPOSE version &> /dev/null; then
    COMPOSE="docker-compose"
fi
DB_USER="gaussdb"
DB_NAME="movie_db"
GS_PASSWORD="GaussDB@2024"

run_gsql() {
    local db="$1"
    local sql="$2"
    docker exec gaussdb bash -lc "export GAUSSHOME=/usr/local/opengauss; export PATH=\$GAUSSHOME/bin:\$PATH; export LD_LIBRARY_PATH=\$GAUSSHOME/lib:\$LD_LIBRARY_PATH; gsql -d '$db' -U '$DB_USER' --password '$GS_PASSWORD' -c \"$sql\""
}

# 1. 检查 Docker
echo "[1/7] 检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi
echo "  Docker 已安装"

# 2. 停止旧容器
echo "[2/7] 停止旧容器..."
$COMPOSE -f docker-compose.prod.yml down 2>/dev/null
docker rm -f gaussdb 2>/dev/null

# 3. 启动 GaussDB (轻量化)
echo "[3/7] 启动 GaussDB (内存限制 2GB)..."
$COMPOSE -f docker-compose.prod.yml up -d gaussdb

# 4. 等待 GaussDB 启动
echo "[4/7] 等待 GaussDB 启动 (约60秒)..."
for i in {1..90}; do
    if run_gsql postgres "SELECT 1;" &>/dev/null; then
        echo "  GaussDB 已就绪!"
        break
    fi
    if [ $i -eq 90 ]; then
        echo "  超时，请检查日志: docker logs gaussdb"
        exit 1
    fi
    sleep 2
done

# 5. 创建业务数据库；表结构由 Flask/SQLAlchemy 首次启动自动创建
echo "[5/7] 创建业务数据库..."
if run_gsql postgres "SELECT 1 FROM pg_database WHERE datname='$DB_NAME';" | grep -q "(1 row)"; then
    echo "  数据库 $DB_NAME 已存在"
else
    run_gsql postgres "CREATE DATABASE $DB_NAME ENCODING 'UTF8' TEMPLATE template0;"
    echo "  数据库 $DB_NAME 创建完成"
fi

# 6. 构建并启动后端和前端
echo "[6/7] 构建并启动后端和前端..."
$COMPOSE -f docker-compose.prod.yml up -d --build backend frontend

echo "[7/7] 等待服务启动..."
sleep 30
docker exec movie-backend python seed_data.py || echo "  种子数据已存在或初始化失败，请按需查看后端日志"
docker exec movie-backend python sync_posters.py || echo "  海报路径同步失败，请按需查看后端日志"

echo ""
echo "=========================================="
echo "  部署完成！"
echo "=========================================="
echo ""
echo "访问地址: http://$(curl -s ifconfig.me)"
echo ""
echo "测试账号: alice / 123456"
echo ""
echo "查看状态: $COMPOSE -f docker-compose.prod.yml ps"
echo "查看日志: $COMPOSE -f docker-compose.prod.yml logs -f"
echo ""
