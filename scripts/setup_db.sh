#!/bin/bash

# 设置错误时退出
set -e

# 显示执行命令
set -x

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 等待数据库服务启动
echo "等待数据库服务启动..."
sleep 10

# 创建数据库
echo "创建数据库..."
docker-compose exec db mysql -uroot -proot -e "CREATE DATABASE IF NOT EXISTS credit_card_db;"
docker-compose exec db mysql -uroot -proot -e "CREATE DATABASE IF NOT EXISTS vector_db;"

# 初始化数据库表
echo "初始化数据库表..."
docker-compose exec backend python -c "
from sqlalchemy import create_engine
from knowledge_base.models import Base
from config import settings

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(engine)
"

# 初始化向量数据库
echo "初始化向量数据库..."
docker-compose exec backend python -c "
from sqlalchemy import create_engine
from knowledge_base.models import Base
from config import settings

engine = create_engine(settings.VECTOR_DB_URL)
Base.metadata.create_all(engine)
"

echo "数据库初始化完成！" 