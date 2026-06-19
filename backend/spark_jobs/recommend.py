"""
Spark ALS 协同过滤推荐算法
从 GaussDB 读取评分数据 -> 训练 ALS 模型 -> 预测评分 -> 写回数据库
"""
import os
import sys

# 将项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.sql.types import IntegerType, FloatType, StructType, StructField
from pyspark.sql.functions import explode, col

# 数据库配置（从环境变量读取）
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', '5432')),
    'dbname': os.environ.get('DB_NAME', 'postgres'),
    'user': os.environ.get('DB_USER', 'gaussadmin'),
    'password': os.environ.get('DB_PASSWORD', 'GaussDB@2024'),
}


def get_spark_session():
    """创建 Spark 会话（轻量化配置）"""
    return SparkSession.builder \
        .appName("MovieRecommender") \
        .master("local[1]") \
        .config("spark.driver.memory", "512m") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()


def load_ratings_from_db(spark):
    """从数据库加载评分数据"""
    import psycopg2
    import psycopg2.extensions
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)

    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        options='-c client_encoding=UTF8'
    )
    cur = conn.cursor()
    cur.execute("SELECT user_id, movie_id, score FROM ratings")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    print(f"  Loaded {len(rows)} ratings from DB")

    schema = StructType([
        StructField("user_id", IntegerType(), True),
        StructField("movie_id", IntegerType(), True),
        StructField("score", FloatType(), True),
    ])
    return spark.createDataFrame(rows, schema=schema)


def save_recommendations_to_db(recommendations):
    """将推荐结果写回数据库"""
    import psycopg2

    conn = psycopg2.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        dbname=DB_CONFIG['dbname'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        options='-c client_encoding=UTF8'
    )
    cur = conn.cursor()

    # 清除旧的 ALS 推荐
    cur.execute("DELETE FROM recommendations WHERE algorithm = 'als'")

    # 写入新推荐
    for rec in recommendations:
        cur.execute(
            "INSERT INTO recommendations (user_id, movie_id, score, algorithm) VALUES (%s, %s, %s, 'als')",
            rec
        )
    conn.commit()

    cur.close()
    conn.close()


def main():
    print("=" * 50)
    print("Spark ALS Recommendation Engine")
    print("=" * 50)

    spark = get_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    # 1. Load data
    print("[1/4] Loading ratings...")
    ratings_df = load_ratings_from_db(spark)
    count = ratings_df.count()
    print(f"  Total: {count} ratings")

    if count < 10:
        print("  Not enough ratings (<10), skipping")
        spark.stop()
        return

    # 2. Train ALS
    print("[2/4] Training ALS model...")
    als = ALS(
        maxIter=10,
        regParam=0.1,
        rank=10,
        userCol="user_id",
        itemCol="movie_id",
        ratingCol="score",
        coldStartStrategy="drop",
        nonnegative=True
    )
    model = als.fit(ratings_df)
    print("  Model trained")

    # 3. Generate recommendations
    print("[3/4] Generating recommendations...")
    user_recs = model.recommendForAllUsers(10)

    recs_flat = user_recs.select(
        col("user_id"),
        explode(col("recommendations")).alias("rec")
    ).select(
        col("user_id"),
        col("rec.movie_id").alias("movie_id"),
        col("rec.rating").alias("score")
    )

    recs_list = recs_flat.collect()
    recommendations = [(r.user_id, r.movie_id, float(r.score)) for r in recs_list]
    print(f"  Generated {len(recommendations)} recommendations")

    # 4. Save to DB
    print("[4/4] Saving to database...")
    save_recommendations_to_db(recommendations)
    print(f"  Done!")

    print("=" * 50)
    print("ALS recommendation complete!")
    print("=" * 50)

    spark.stop()


if __name__ == '__main__':
    main()
