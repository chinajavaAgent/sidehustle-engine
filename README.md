# 副业有道内容引擎 (SideHustleEngine)

一个基于Vue3 + FastAPI的自动化内容生产系统MVP版本。

## 功能特性

- 🎯 **智能选题推荐**: 基于热点趋势和市场需求的选题生成
- ✍️ **AI内容生成**: 支持多种文章框架的智能内容创作
- 🎨 **可视化界面**: 基于Vue3 + TailwindCSS的现代化用户界面
- ⚡ **实时生成**: 快速响应的内容生成和优化功能

## 技术栈

### 前端
- Vue 3.5+
- Vite 6.3+
- TailwindCSS 4.1+
- Headless UI

### 后端
- FastAPI 0.104+
- Python 3.8+
- Pydantic 2.5+

## 快速开始

### 环境要求
- Node.js 16+
- Python 3.8+

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd sidehustle-engine
```

2. **启动后端服务**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
python main.py
```

3. **启动前端服务**
```bash
cd frontend
npm install
npm run dev
```

4. **访问应用**
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
sidehustle-engine/
├── frontend/                 # Vue3前端应用
│   ├── src/
│   │   ├── components/      # 组件
│   │   ├── styles/         # 样式文件
│   │   └── App.vue         # 主应用
│   ├── package.json
│   └── vite.config.js
├── backend/                 # FastAPI后端服务
│   ├── api/                # API路由
│   ├── core/               # 核心配置
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑
│   ├── requirements.txt
│   └── main.py
└── README.md
```

## API接口

### 选题相关
- `GET /api/topics/trending` - 获取热门选题
- `GET /api/topics/search` - 搜索选题
- `GET /api/topics/categories` - 获取分类列表

### 内容生成
- `POST /api/content/generate` - 生成文章内容
- `GET /api/content/frameworks` - 获取文章框架
- `POST /api/content/optimize/title` - 优化标题

## 使用说明

1. **选择选题**: 在左侧面板查看推荐选题，点击选择
2. **选择框架**: 选择适合的文章框架模板
3. **生成内容**: 点击"生成文章"按钮，AI将自动创作内容
4. **优化内容**: 使用标题优化、内容润色等功能完善文章

## 配置说明

### 环境变量
复制 `backend/.env.example` 为 `backend/.env` 并配置：

```env
OPENAI_API_KEY=your_openai_api_key_here
API_TITLE=副业有道内容引擎
API_VERSION=1.0.0
```

## 开发计划

### MVP版本 (当前)
- [x] 基础项目结构
- [x] 选题推荐功能
- [x] 内容生成功能
- [x] 基础UI界面

### 下一版本
- [ ] 集成真实AI API
- [ ] 素材聚合功能
- [ ] 排版和格式化
- [ ] 用户认证系统

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License