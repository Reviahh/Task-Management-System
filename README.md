# 智能任务管理系统 (Intelligent Task Management System)

## Role Track
**AI/LLM 开发者赛道**

## Tech Stack
- **后端语言**: Python 3.10+
- **后端框架**: FastAPI
- **前端框架**: Vue 3 + TypeScript
- **样式**: Tailwind CSS
- **状态管理**: Pinia
- **数据库**: SQLite (异步 aiosqlite)
- **AI/LLM**: OpenAI API (支持兼容接口)
- **其他工具**: SQLAlchemy (ORM), Pydantic (数据验证)

## Features Implemented

### Core Features (核心功能)
- [x] Task CRUD 操作 (创建、读取、更新、删除)
- [x] 任务属性: id, title, description, status, priority, created_at, updated_at, tags
- [x] 数据持久化 (SQLite)
- [x] 任务过滤 (按状态、优先级、标签)
- [x] 任务排序 (创建时间、更新时间、优先级、标题)
- [x] 分页支持
- [x] 关键词搜索

### AI/LLM Features (AI 功能)
- [x] **自然语言任务解析**: 从自然语言输入中提取任务标题、描述、优先级、标签、截止日期
- [x] **智能标签建议**: 基于任务内容自动推荐相关标签
- [x] **优先级推荐**: 分析任务内容智能推荐优先级
- [x] **任务分解**: 将复杂任务拆分为可执行的子任务
- [x] **语义搜索**: 基于语义相似度搜索任务，而非仅关键词匹配
- [x] **任务摘要**: AI 生成任务统计和洞察摘要

### Frontend Features (前端功能)
- [x] 现代化响应式 UI 设计
- [x] 任务列表视图
- [x] 任务创建/编辑表单
- [x] 过滤和排序控件
- [x] 实时搜索
- [x] AI 功能专属界面
- [x] 任务统计仪表板
- [x] 流畅的动画和过渡效果
- [x] 深色主题设计

## Project Structure
```
project/
├── README.md
├── .gitignore
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库配置
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── task.py          # Task 数据模型
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── task.py          # Pydantic schemas
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── tasks.py         # API 路由
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── task_service.py  # 任务业务逻辑
│   │       └── ai_service.py    # AI 功能服务
│   └── tasks.db                 # SQLite 数据库 (运行后生成)
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── main.ts
        ├── style.css
        ├── App.vue
        ├── types/
        │   └── task.ts          # TypeScript 类型定义
        ├── api/
        │   └── tasks.ts         # API 客户端
        ├── stores/
        │   └── tasks.ts         # Pinia store
        └── components/
            ├── TaskList.vue     # 任务列表组件
            ├── TaskForm.vue     # 任务表单组件
            ├── FilterBar.vue    # 过滤栏组件
            ├── AIFeatures.vue   # AI 功能组件
            └── TaskSummary.vue  # 任务摘要组件
```

## Setup Instructions

### Prerequisites (前置要求)
- Python 3.10+
- Node.js 18+
- npm 或 yarn
- OpenAI API Key (可选，用于 AI 功能)

### Backend Setup (后端设置)

1. 进入后端目录并创建虚拟环境:
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 配置环境变量 (创建 `.env` 文件):
```bash
# OpenAI API Configuration (可选)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./tasks.db

# Application Settings
DEBUG=true
```

4. 启动后端服务:
```bash
uvicorn app.main:app --reload --port 8000
```

后端 API 文档: http://localhost:8000/docs

### Frontend Setup (前端设置)

1. 进入前端目录并安装依赖:
```bash
cd frontend
npm install
```

2. 启动开发服务器:
```bash
npm run dev
```

前端访问地址: http://localhost:3000

## API Documentation

### Task Endpoints (任务接口)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks/` | 创建新任务 |
| GET | `/api/tasks/` | 获取任务列表 (支持分页、过滤、排序) |
| GET | `/api/tasks/{id}` | 获取单个任务 |
| PUT | `/api/tasks/{id}` | 更新任务 |
| DELETE | `/api/tasks/{id}` | 删除任务 |

### AI Endpoints (AI 接口)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks/ai/parse` | 解析自然语言输入 |
| POST | `/api/tasks/ai/create-from-text` | 从自然语言创建任务 |
| POST | `/api/tasks/{id}/ai/suggest-tags` | 获取标签建议 |
| POST | `/api/tasks/{id}/ai/suggest-priority` | 获取优先级建议 |
| POST | `/api/tasks/{id}/ai/breakdown` | 任务分解 |
| POST | `/api/tasks/ai/semantic-search` | 语义搜索 |
| POST | `/api/tasks/ai/summary` | 获取任务摘要 |

### Request/Response Examples

#### 创建任务
```bash
POST /api/tasks/
Content-Type: application/json

{
  "title": "完成项目文档",
  "description": "编写 README 和 API 文档",
  "priority": "high",
  "tags": ["documentation", "project"]
}
```

#### 自然语言解析
```bash
POST /api/tasks/ai/parse
Content-Type: application/json

{
  "text": "明天下午3点提醒我去开会，这很重要"
}

Response:
{
  "title": "去开会",
  "description": null,
  "priority": "high",
  "tags": ["meeting"],
  "due_date": "2024-01-05 15:00",
  "confidence": 0.85
}
```

#### 语义搜索
```bash
POST /api/tasks/ai/semantic-search
Content-Type: application/json

{
  "query": "关于代码的任务",
  "limit": 10
}
```

## Design Decisions (设计决策)

### 1. 技术选型
- **FastAPI**: 选择 FastAPI 因为其高性能、自动 API 文档生成、原生异步支持
- **Vue 3 + TypeScript**: 提供更好的类型安全和开发体验
- **SQLite**: 简单部署，适合演示项目，易于切换到其他数据库
- **Tailwind CSS**: 快速构建现代化 UI，高度可定制

### 2. AI 功能实现
- **双重策略**: 同时支持 OpenAI API 和本地 fallback 方案
- **Fallback 机制**: 当 API 不可用时，使用基于规则的本地解析
- **嵌入存储**: 在数据库中存储文本嵌入向量，支持语义搜索
- **简化向量存储**: 使用 JSON 字段存储嵌入，避免额外的向量数据库依赖

### 3. 架构设计
- **服务层分离**: AI 服务和任务服务分离，便于维护和测试
- **异步优先**: 全异步设计，提高并发处理能力
- **类型安全**: 使用 Pydantic 进行数据验证，TypeScript 用于前端类型安全

## Challenges & Solutions (挑战与解决方案)

### 1. AI API 可用性
**挑战**: 用户可能没有 OpenAI API Key
**解决**: 实现完整的 fallback 机制，基于关键词和规则的本地解析

### 2. 语义搜索性能
**挑战**: 大量任务时语义搜索可能较慢
**解决**: 预计算并存储嵌入向量，搜索时只计算查询的嵌入

### 3. 前后端类型同步
**挑战**: 保持前后端数据类型一致
**解决**: 使用 TypeScript 接口镜像 Pydantic schemas

## Future Improvements (未来改进)

- [ ] 用户认证和授权系统
- [ ] 任务依赖关系管理
- [ ] 实时协作 (WebSocket)
- [ ] 向量数据库集成 (ChromaDB/FAISS) 提升搜索性能
- [ ] 任务模板功能
- [ ] 导出功能 (JSON/CSV/PDF)
- [ ] 多语言支持
- [ ] 移动端适配优化
- [ ] 单元测试和集成测试
- [ ] Docker 容器化部署
- [ ] CI/CD 流程

## Known Limitations (已知限制)

1. **语义搜索**: 当前使用简化的向量相似度计算，大规模数据时性能可能下降
2. **AI 功能**: 依赖外部 API，网络不稳定时可能影响体验
3. **数据库**: SQLite 适合小规模使用，生产环境建议切换到 PostgreSQL
4. **无实时更新**: 当前未实现 WebSocket，多用户场景需要手动刷新

## Time Spent
约 3-4 小时

## AI Assistant Usage
本项目使用 AI 辅助开发，主要用于:
- 代码结构设计建议
- 代码生成和优化
- 文档编写

最终代码经过人工审核和调整。
