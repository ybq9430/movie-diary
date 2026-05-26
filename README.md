# Movie Diary - 个人观影记录系统

一个完整的观影记录管理平台，支持从豆瓣抓取观影数据、手动添加电影、AI 分析观影性格、智能推荐等功能。
<img width="1695" height="1031" alt="image" src="https://github.com/user-attachments/assets/4b827736-acd8-4864-8f7e-9d7e68bb3d2f" />
<img width="1622" height="1042" alt="image" src="https://github.com/user-attachments/assets/806aacc4-c231-4ffe-9ad6-bba6d9217f91" />
<img width="1869" height="1026" alt="image" src="https://github.com/user-attachments/assets/27a75cd4-eedc-43a1-8bf3-adbf26f808d8" />




## 功能特性

### 数据管理
- **豆瓣抓取** — 输入豆瓣用户 ID，自动抓取观影记录（标题、评分、导演、演员、类型、观影日期等）
- **CSV 导入** — 支持导入豆瓣导出的 CSV 文件，自动去重
- **手动添加** — 手动录入电影信息，支持自定义标签
- **豆瓣数据补充** — 为缺少海报和简介的电影自动补充数据
- **TMDB 搜索** — 通过 TMDB API 搜索电影海报和详情

### 观影管理
- **电影目录** — 分页浏览、按类型/年份/地区/评分筛选、搜索、排序
- **电影详情** — 查看完整信息、编辑评分/短评/观影日期、收藏管理
- **相似推荐** — 基于类型/导演/地区的本地相似度算法

### 数据统计
- **总览面板** — 观影总数、平均评分、最爱类型、累计时长
- **评分分布** — 1-5 星评分统计
- **类型偏好** — 最常看的电影类型
- **导演排行** — 最常看的导演
- **地区分布** — 观影地区统计
- **观影趋势** — 按月观影数量变化
- **月份偏好** — 各月份观影习惯
- **年代分布** — 按十年分组的观影分布

### AI 功能
- **观影性格分析** — 根据观影历史生成个性化人格分析报告
- **AI 肖像** — 生成观影人格艺术肖像（支持多种风格）
- **智能推荐** — 基于观影偏好推荐未看过的电影

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + ECharts + Pinia |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| AI | MiMo API（Anthropic 兼容接口） |
| 海报 | TMDB API + 豆瓣海报代理 |
| 抓取 | requests + BeautifulSoup4 |

## 项目结构

```
05 - douban/
├── backend/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置（API 密钥、路径、抓取参数）
│   ├── database.py          # SQLAlchemy 数据库连接
│   ├── models.py            # 数据模型（Movie, MovieTag, AI*）
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── utils.py             # 共享工具函数
│   ├── routers/
│   │   ├── movies.py        # 电影 CRUD API
│   │   ├── ai.py            # AI 分析 API
│   │   ├── import_router.py # CSV 导入 + 豆瓣数据补充
│   │   ├── stats.py         # 统计分析 API
│   │   ├── tmdb_router.py   # TMDB 代理 API
│   │   └── scrape_router.py # 豆瓣抓取 API
│   ├── services/
│   │   ├── movie_service.py      # 电影业务逻辑
│   │   ├── ai_service.py         # AI 调用封装
│   │   ├── douban_data_service.py # 相似电影算法
│   │   ├── tmdb_service.py       # TMDB API 封装
│   │   └── stats_service.py      # 统计查询
│   └── static/              # 静态文件（上传、导出）
├── frontend/
│   ├── src/
│   │   ├── views/           # 页面组件（9 个页面）
│   │   ├── components/      # 复用组件（MovieCard, AppSidebar 等）
│   │   ├── stores/          # Pinia 状态管理
│   │   ├── api/             # Axios API 封装
│   │   └── router/          # Vue Router 配置
│   └── package.json
├── scraper.py               # 豆瓣观影记录抓取脚本
├── config.py                # 根配置（加载 backend/config.py）
├── requirements.txt         # Python 依赖
├── start.bat                # Windows 一键启动脚本
└── output/                  # 抓取输出目录
```

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm 或 pnpm

### 1. 安装后端依赖

```bash
pip install -r requirements.txt
pip install fastapi uvicorn sqlalchemy httpx pydantic
```

### 2. 安装前端依赖

```bash
cd frontend
npm install
```

### 3. 配置环境变量（可选）

创建 `.env` 文件或设置系统环境变量：

```bash
# AI 功能（可选，不配置则 AI 功能不可用）
MIMO_API_KEY=your_mimo_api_key
MIMO_BASE_URL=https://token-plan-cn.xiaomimimo.com/anthropic
MIMO_MODEL=mimo-v2.5-pro

# TMDB API（可选，不配置则海报搜索不可用）
TMDB_API_KEY=your_tmdb_api_key
```

### 4. 启动项目

**方式一：一键启动（Windows）**

```bash
start.bat
```

**方式二：分别启动**

```bash
# 终端 1 — 后端
cd backend
python -m uvicorn main:app --reload --port 8000

# 终端 2 — 前端
cd frontend
npm run dev
```

### 5. 访问

| 服务 | 地址 |
|------|------|
| 前端 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档（Swagger） | http://localhost:8000/docs |
| API 文档（ReDoc） | http://localhost:8000/redoc |

## 使用指南

### 从豆瓣抓取数据

1. 进入「数据抓取」页面
2. 输入豆瓣用户 ID（数字，可在个人主页 URL 中找到）
3. （可选）填入 Cookie 以访问更多数据
4. 点击「开始抓取」，等待完成
5. 查看结果表格，可下载 CSV 文件

### 导入 CSV

1. 进入「数据导入」页面
2. 拖拽或选择 CSV 文件
3. 点击「导入上传的文件」
4. 等待导入完成

### AI 分析

1. 确保已配置 `MIMO_API_KEY`
2. 进入「观影性格」页面，点击生成分析
3. 进入「AI 肖像」页面，选择风格生成肖像
4. 进入「智能推荐」页面，获取个性化推荐

## API 端点

### 电影 `/api/movies`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/movies` | 电影列表（分页、筛选、排序） |
| GET | `/api/movies/{id}` | 电影详情 |
| POST | `/api/movies` | 手动添加电影 |
| PUT | `/api/movies/{id}` | 更新电影 |
| DELETE | `/api/movies/{id}` | 删除电影 |
| GET | `/api/movies/{id}/similar` | 相似电影 |

### 统计 `/api/stats`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stats/overview` | 总览数据 |
| GET | `/api/stats/rating-distribution` | 评分分布 |
| GET | `/api/stats/genre-preference` | 类型偏好 |
| GET | `/api/stats/director-ranking` | 导演排行 |
| GET | `/api/stats/region-distribution` | 地区分布 |
| GET | `/api/stats/watching-trend` | 观影趋势 |
| GET | `/api/stats/monthly-pattern` | 月份偏好 |
| GET | `/api/stats/year-distribution` | 年代分布 |

### 抓取 `/api/scrape`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/scrape` | 启动抓取任务 |
| GET | `/api/scrape/status` | 轮询抓取进度 |
| GET | `/api/scrape/results` | 分页查看结果 |
| GET | `/api/scrape/download` | 下载 CSV |

### 导入 `/api/import`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/import/csv` | 导入默认 CSV |
| POST | `/api/import/csv/upload` | 上传并导入 CSV |
| GET | `/api/import/status` | 导入进度 |
| POST | `/api/import/enrich` | 豆瓣数据补充 |
| GET | `/api/import/enrich/status` | 补充进度 |

### AI `/api/ai`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/personality` | 生成观影性格分析 |
| GET | `/api/ai/personality/latest` | 获取最新分析 |
| POST | `/api/ai/portrait` | 生成 AI 肖像 |
| GET | `/api/ai/portrait/latest` | 获取最新肖像 |
| POST | `/api/ai/recommend` | 生成智能推荐 |
| GET | `/api/ai/recommend/latest` | 获取最新推荐 |

### 其他

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/poster?url=` | 海报代理（防盗链绕过） |
| GET | `/api/tmdb/search?q=` | TMDB 电影搜索 |
| GET | `/api/tmdb/movie/{id}` | TMDB 电影详情 |

## 数据库

SQLite 数据库文件位于 `backend/data/movie_diary.db`，包含以下表：

| 表名 | 说明 |
|------|------|
| `movies` | 电影主表（标题、年份、类型、导演、评分等） |
| `movie_tags` | 电影标签（多对多） |
| `ai_personality` | AI 性格分析历史 |
| `ai_portrait` | AI 肖像历史 |
| `ai_recommendation` | AI 推荐历史 |

## 注意事项

- 豆瓣抓取有频率限制，默认间隔 5-8 秒，详情页 3-5 秒
- 海报代理仅允许访问 `movie.douban.com` 和 `doubanio.com` 域名
- AI 功能需要有效的 MiMo API 密钥
- TMDB 搜索需要有效的 TMDB API 密钥
- 上传 CSV 文件大小限制为 10MB
