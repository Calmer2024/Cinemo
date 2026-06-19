# Cinemo — 智能电影推荐系统

> 基于 Vue 3 + Flask + PySpark ALS 协同过滤的全栈电影推荐平台

一个集电影浏览、评分、个性化推荐和数据可视化于一体的 Web 应用。用户可以浏览 30 部经典电影的详细信息，给出 1-5 星评分，系统通过 Apache Spark ALS 算法为每位用户生成个性化推荐，并提供 ECharts 数据看板。

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [生产部署](#生产部署)
- [API 文档](#api-文档)
- [推荐算法](#推荐算法)
- [测试账号](#测试账号)
- [端口说明](#端口说明)

## 功能特性

- **电影目录浏览** — 网格布局展示电影海报，支持按标题/导演/演员搜索、类型筛选、评分/年份/标题排序、分页浏览
- **用户认证系统** — JWT 注册与登录（7 天有效期），路由守卫保护受限页面
- **电影评分系统** — 1-5 星评分 + 可选文字评论，每人每片仅一条评分（自动更新），平均分实时重算
- **个性化推荐** — 三级回退策略：ALS 协同过滤 → 基于内容的推荐 → 热门电影推荐
- **相似电影推荐** — 电影详情页基于类型相似度推荐相关影片
- **数据看板** — ECharts 可视化：评分分布柱状图、类型占比环形图、总电影/评分/用户数统计卡片
- **用户中心** — 查看和管理个人评分历史，支持删除评分
- **暗色影院风格 UI** — 深色主题 + 琥珀色点缀，流畅动画，响应式布局（移动端汉堡菜单）

## 技术栈

| 层级 | 技术 |
|------|------|
| **前端** | Vue 3 (Composition API) · Vite · Element Plus · ECharts · Axios · Vue Router |
| **后端** | Flask · Flask-SQLAlchemy · PyJWT · Flask-CORS · Gunicorn |
| **推荐引擎** | Apache Spark (PySpark ALS 协同过滤) |
| **数据库** | PostgreSQL 15 (开发) / openGauss 5.0 (生产) |
| **容器化** | Docker · Docker Compose · nginx |
| **部署目标** | 华为云开发者空间 |

## 项目结构

```
movie-recommender/
├── docker-compose.yml               # 本地开发环境 (PostgreSQL)
├── docker-compose.prod.yml          # 生产环境 (openGauss)
├── deploy.sh                        # 华为云一键部署脚本
├── DEPLOY.md                        # 华为云部署详细指南
│
├── backend/
│   ├── Dockerfile
│   ├── app.py                       # Flask 应用工厂 + openGauss 兼容补丁
│   ├── config.py                    # 环境变量配置 (数据库/JWT/Spark)
│   ├── models.py                    # 数据模型: User, Movie, Rating, Recommendation
│   ├── requirements.txt
│   ├── seed_data.py                 # 种子数据: 30 部电影 + 测试用户 + 模拟评分
│   ├── routes/
│   │   ├── auth.py                  # 认证路由: 注册/登录/个人信息
│   │   ├── movies.py                # 电影 CRUD + 搜索/筛选/排序/分页
│   │   ├── ratings.py               # 评分增删改查
│   │   └── recommendations.py       # 推荐 + 相似电影 + 数据看板
│   └── spark_jobs/
│       └── recommend.py             # PySpark ALS 协同过滤任务
│
└── frontend/
    ├── Dockerfile                   # 多阶段构建: Node 编译 + nginx 部署
    ├── nginx.conf                   # SPA history 模式 + API 反向代理
    ├── package.json
    ├── vite.config.js
    ├── public/
    │   └── posters/                 # 30 张电影海报图片
    └── src/
        ├── main.js
        ├── App.vue                  # 根组件: 导航栏/用户菜单/页脚
        ├── style.css                # 全局设计系统 (暗色影院主题)
        ├── api/index.js             # Axios 客户端 + JWT 拦截器
        ├── router/index.js          # Vue Router + 认证守卫
        └── views/
            ├── Home.vue             # 电影目录页
            ├── Login.vue            # 登录页
            ├── Register.vue         # 注册页
            ├── MovieDetail.vue      # 电影详情 + 评分 + 相似推荐
            ├── Recommend.vue        # 个性化推荐页
            ├── Dashboard.vue        # 数据看板
            └── MyRatings.vue        # 我的评分
```

## 快速开始

### 环境要求

- Docker 及 Docker Compose
- （不使用 Docker 时）Python 3.11+ / Node.js 22+

### Docker 一键启动

```bash
git clone https://github.com/Calmer2024/movie-recommender.git
cd movie-recommender
docker-compose up -d --build
```

启动后会运行三个容器：

| 容器 | 端口 | 说明 |
|------|------|------|
| gaussdb | 5433 | PostgreSQL 15 数据库 |
| movie-backend | 5000 | Flask REST API |
| movie-frontend | 80 | nginx 前端服务 |

### 初始化数据

容器启动完成后，导入种子数据（30 部电影 + 测试用户 + 模拟评分）：

```bash
pip install psycopg werkzeug
cd backend
python seed_data.py
```

访问 `http://localhost` 即可使用。

### 前端独立开发

```bash
cd frontend
npm install
npm run dev
```

Vite 开发服务器运行在 `http://localhost:3000`，自动将 `/api` 请求代理到后端 `localhost:5000`。

## 生产部署

项目提供了面向华为云开发者空间的一键部署脚本：

```bash
chmod +x deploy.sh
./deploy.sh
```

部署脚本会自动完成：

1. 检查 Docker 环境
2. 停止旧容器
3. 启动 openGauss 数据库（2GB 内存限制）
4. 等待数据库就绪（最长 180 秒）
5. 创建 `movie_db` 数据库
6. 构建并启动后端 + 前端容器
7. 导入种子数据并同步海报

详细的部署说明请参考 [DEPLOY.md](DEPLOY.md)。

## API 文档

### 认证 `/api/auth`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/auth/register` | 用户注册 | ✗ |
| POST | `/api/auth/login` | 用户登录，返回 JWT | ✗ |
| GET | `/api/auth/me` | 获取当前用户信息 | ✓ |
| PUT | `/api/auth/me` | 更新个人信息 | ✓ |

### 电影 `/api/movies`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/movies` | 电影列表（搜索/筛选/排序/分页） | ✗ |
| GET | `/api/movies/genres` | 获取所有电影类型 | ✗ |
| GET | `/api/movies/<id>` | 电影详情 | ✗ |
| POST | `/api/movies` | 创建电影 | ✓ |
| PUT | `/api/movies/<id>` | 更新电影 | ✓ |
| DELETE | `/api/movies/<id>` | 删除电影 | ✓ |

### 评分 `/api/ratings`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| POST | `/api/ratings` | 提交/更新评分 | ✓ |
| GET | `/api/ratings/movie/<id>` | 获取某电影的所有评分 | ✗ |
| GET | `/api/ratings/user` | 获取当前用户的评分 | ✓ |
| DELETE | `/api/ratings/<id>` | 删除评分（仅限本人） | ✓ |

### 推荐 `/api/recommendations`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|------|
| GET | `/api/recommendations` | 获取个性化推荐 | ✓ |
| GET | `/api/recommendations/similar/<id>` | 获取相似电影 | ✗ |
| GET | `/api/recommendations/dashboard` | 数据看板统计 | ✗ |
| POST | `/api/recommendations/trigger` | 手动触发 Spark ALS 计算 | ✓ |

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 服务健康检查 |

## 推荐算法

系统实现三级推荐策略，逐级回退：

```
┌─────────────────────────────────────────────────────┐
│  ① ALS 协同过滤 (主策略)                             │
│     PySpark ALS, maxIter=10, rank=10                │
│     → 为每位用户生成 Top-10 推荐                      │
├─────────────────────────────────────────────────────┤
│  ② 基于内容的推荐 (回退)                              │
│     分析用户高分电影 (≥3.5) 的类型偏好                │
│     → 推荐同类型的未评分电影                           │
├─────────────────────────────────────────────────────┤
│  ③ 热门推荐 (最终回退)                                │
│     → 返回用户未评分的高分电影                         │
└─────────────────────────────────────────────────────┘
```

用户可在推荐页面手动触发 Spark ALS 重新计算。

## 测试账号

种子数据包含 5 个测试用户：

| 用户名 | 密码 |
|--------|------|
| alice | 123456 |
| bob | 123456 |
| charlie | 123456 |
| diana | 123456 |
| eve | 123456 |

## 端口说明

| 服务 | 端口 | 场景 |
|------|------|------|
| PostgreSQL / openGauss | 5433 (开发) / 5432 (生产) | 数据库 |
| Flask 后端 | 5000 | REST API |
| Vue 前端 (nginx) | 80 | Web 界面 |
| Vite 开发服务器 | 3000 | 仅前端开发 |

## 许可证

本项目为武汉大学计算机学院「云计算平台与技术」课程大作业。
