"""
Spark ALS 协同过滤推荐算法
从 GaussDB 读取评分数据 → 训练 ALS 模型 → 预测评分 → 写回数据库
"""
import os
import sys

# 将项目根目录加入路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql.types import IntegerType, FloatType

from config import Config


def get_spark_session():
    """创建 Spark 会话"""
    return SparkSession.builder \
        .appName("MovieRecommender") \
        .master(Config.SPARK_MASTER) \
        .config("spark.jars", "postgresql-42.7.1.jar") \
        .getOrCreate()


def load_ratings_from_db(spark):
    """从 GaussDB 加载评分数据"""
    jdbc_url = Config.SQLALCHEMY_DATABASE_URI.replace('postgresql://', 'jdbc:postgresql://')

    # 解析连接信息
    # 格式: postgresql://user:pass@host:port/db
    uri = Config.SQLALCHEMY_DATABASE_URI
    user_pass = uri.split('://')[1].split('@')[0]
    host_db = uri.split('@')[1]
    user, password = user_pass.split(':')
    host_port, db_name = host_db.split('/')
    host, port = host_port.split(':')

    jdbc_url = f"jdbc:postgresql://{host}:{port}/{db_name}"

    df = spark.read \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "ratings") \
        .option("user", user) \
        .option("password", password) \
        .option("driver", "org.postgresql.Driver") \
        .load()

    return df.select(
        df['user_id'].cast(IntegerType()),
        df['movie_id'].cast(IntegerType()),
        df['score'].cast(FloatType())
    )


def save_recommendations_to_db(recommendations_df, spark):
    """将推荐结果写回 GaussDB"""
    uri = Config.SQLALCHEMY_DATABASE_URI
    user_pass = uri.split('://')[1].split('@')[0]
    host_db = uri.split('@')[1]
    user, password = user_pass.split(':')
    host_port, db_name = host_db.split('/')
    host, port = host_port.split(':')

    jdbc_url = f"jdbc:postgresql://{host}:{port}/{db_name}"

    # 先清除旧的 ALS 推荐
    import psycopg2
    conn = psycopg2.connect(
        host=host, port=port, dbname=db_name,
        user=user, password=password
    )
    cur = conn.cursor()
    cur.execute("DELETE FROM recommendations WHERE algorithm = 'als'")
    conn.commit()

    # 写入新推荐
    recommendations_df.write \
        .format("jdbc") \
        .option("url", jdbc_url) \
        .option("dbtable", "recommendations") \
        .option("user", user) \
        .option("password", password) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

    cur.close()
    conn.close()


def main():
    print("=" * 50)
    print("开始 Spark ALS 推荐计算...")
    print("=" * 50)

    spark = get_spark_session()

    # 1. 加载数据
    print("[1/4] 从 GaussDB 加载评分数据...")
    ratings_df = load_ratings_from_db(spark)
    count = ratings_df.count()
    print(f"  加载了 {count} 条评分记录")

    if count < 10:
        print("  评分数据不足，跳过推荐计算")
        spark.stop()
        return

    # 2. 训练 ALS 模型
    print("[2/4] 训练 ALS 协同过滤模型...")
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

    # 3. 为所有用户生成 Top 10 推荐
    print("[3/4] 生成用户推荐列表...")
    user_recs = model.recommendForAllUsers(10)

    # 展平推荐结果
    from pyspark.sql.functions import explode, col, lit
    recs_flat = user_recs.select(
        col("user_id"),
        explode(col("recommendations")).alias("rec")
    ).select(
        col("user_id"),
        col("rec.movie_id").alias("movie_id"),
        col("rec.rating").alias("score")
    )

    # 添加算法标识
    from pyspark.sql.functions import current_timestamp
    recs_final = recs_flat.withColumn("algorithm", lit("als")) \
                          .withColumn("created_at", current_timestamp())

    # 4. 写回数据库
    print("[4/4] 将推荐结果写入 GaussDB...")
    save_recommendations_to_db(recs_final, spark)

    rec_count = recs_final.count()
    print(f"  写入了 {rec_count} 条推荐记录")

    print("=" * 50)
    print("推荐计算完成！")
    print("=" * 50)

    spark.stop()


if __name__ == '__main__':
    main()
