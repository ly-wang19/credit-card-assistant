# 使用Node.js 16作为基础镜像
FROM node:16-alpine as build-stage

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY frontend/package*.json ./

# 安装依赖
RUN npm install

# 复制源代码
COPY frontend/ .

# 构建应用
RUN npm run build

# 使用Nginx作为生产环境
FROM nginx:stable-alpine as production-stage

# 复制构建文件到Nginx目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制Nginx配置
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"] 