# 信用卡用卡助手智能体

一个基于AI的信用卡推荐和咨询系统，帮助用户找到最适合的信用卡。

## 功能特点

- 智能信用卡推荐
- 多维度信用卡比较
- 专业用卡咨询
- 实时权益查询
- 个性化建议

## 技术栈

### 后端
- FastAPI
- SQLAlchemy
- pgvector
- DeepSeek API
- LangChain

### 前端
- Vue 3
- Element Plus
- Pinia
- Vue Router

### 数据库
- MySQL
- PostgreSQL (pgvector)

## 项目结构

```
credit-card-assistant/
├── backend/                  # 后端服务
│   ├── api/                  # FastAPI接口
│   ├── crawler/              # 爬虫模块
│   ├── data_processor/       # 数据处理
│   ├── knowledge_base/       # 知识库管理
│   ├── llm_service/          # LLM服务
│   ├── rag_service/          # RAG服务
│   └── agent/                # 智能体核心
├── frontend/                 # 前端应用
│   ├── src/
│   │   ├── components/       # Vue组件
│   │   ├── router/           # 路由配置
│   │   ├── stores/           # 状态管理
│   │   └── views/            # 页面视图
├── docker/                   # Docker配置
└── scripts/                  # 实用脚本
```

## 安装部署

### 环境要求
- Docker
- Docker Compose
- Node.js 16+
- Python 3.9+

### 快速开始

1. 克隆项目
```bash
git clone https://github.com/your-username/credit-card-assistant.git
cd credit-card-assistant
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置必要的环境变量
```

3. 启动服务
```bash
# 构建并启动所有服务
./scripts/deploy.sh

# 初始化数据库
./scripts/setup_db.sh
```

4. 访问应用
- 前端: http://localhost:80
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 开发指南

### 后端开发
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### 前端开发
```bash
cd frontend
npm install
npm run dev
```

## 测试

### 后端测试
```bash
cd backend
pytest
```

### 前端测试
```bash
cd frontend
npm run test
```

## 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目维护者: [Your Name](mailto:your.email@example.com)
- 项目链接: https://github.com/your-username/credit-card-assistant 