FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.11-slim

WORKDIR /app

# psycopg2-binary 自带预编译驱动，无需安装系统依赖
ENV PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.aliyun.com

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "app:create_app()"]
