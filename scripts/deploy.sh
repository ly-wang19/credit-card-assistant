#!/bin/bash

# 设置错误时退出
set -e

# 显示执行命令
set -x

# 切换到项目根目录
cd "$(dirname "$0")/.."

# 构建Docker镜像
docker-compose build

# 启动服务
docker-compose up -d

# 等待服务启动
sleep 10

# 检查服务状态
docker-compose ps

# 显示日志
docker-compose logs -f 