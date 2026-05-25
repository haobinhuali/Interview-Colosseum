# AI智能面试系统 (Interview Colosseum)

> 基于多智能体编排 + RAG智能题库 + Pydantic状态契约的工业级AI面试系统

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.4+-brightgreen.svg)](https://vuejs.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-orange.svg)](https://python.langchain.com/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.4+-purple.svg)](https://www.trychroma.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 项目简介

Interview Colosseum 是一个全栈 AI 智能面试系统，模拟真实技术面试流程。系统通过三个专业 Agent（技术面、压力面、综合面）对候选人进行多轮深度追问，结合 RAG 智能题库去重检索和 SQLite 断点续考机制，提供工业级的面试体验。

### 核心特性

- **多智能体面试编排**：技术面 → 压力面 → 综合面，三阶段自适应路由，每阶段最多 8 轮深度追问
- **RAG 智能题库三层去重**：主过滤器 + 内存 Set 精确去重 + Fallback 二次去重，跨阶段绝对不撞题
- **Pydantic 状态契约**：强类型状态管理 + 评估数据校验（分数范围/枚举值），替代弱类型 TypedDict
- **SQLite 断点续考**：网络异常或主动中断后完美恢复会话，继承已问题目 ID 和历史对话
- **内存缓存 TTL + LRU**：OrderedDict 实现 1 小时过期自动清理，最大容量 100 条，防止内存泄漏
- **LLM 重试机制**：指数退避重试装饰器（3 次重试，1s → 2s → 4s），提高网络抖动时的稳定性
- **RAG 性能监控**：每次检索记录耗时（elapsed_ms），便于性能调优
- **加权综合评估**：技术深度 40% + 抗压能力 30% + 逻辑表达 15% + 诚信度 15%
- **ECharts 雷达图**：能力画像可视化，直观展示面试评估结果
- **Docker 一键部署**：前后端服务容器化，支持生产环境交付

---

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端层 (Vue3 + ECharts)               │
│  - 面试交互界面    - 雷达图可视化    - 简历上传组件       │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (FastAPI REST API)
┌────────────────────────▼────────────────────────────────┐
│                   后端层 (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐ │
│  │ 路由层        │  │ 配置层        │  │ 工具层         │ │
│  │ - interview   │  │ - LLM配置     │  │ - retry重试   │ │
│  │ - resume      │  │ - Agent温度   │  │ - db会话管理  │ │
│  │ - question    │  │              │  │ - resume解析  │ │
│  └──────┬───────┘  └──────────────┘  └───────────────┘ │
│         │                                               │
│  ┌──────▼──────────────────────────────────────────┐   │
│  │           核心编排层 (Orchestrator)               │   │
│  │  - InterviewState (Pydantic BaseModel)           │   │
│  │  - 阶段路由 (TECH → PRESSURE → COMPREHENSIVE)    │   │
│  │  - 轮数控制 (max 8轮/阶段)                        │   │
│  │  - 内存缓存 (OrderedDict + TTL 1h + LRU)         │   │
│  │  - 状态同步 (_sync_asked_ids)                     │   │
│  └──────┬──────────────────────────────────────────┘   │
│         │                                               │
│  ┌──────▼──────────────────────────────────────────┐   │
│  │           节点层 (Nodes)                          │   │
│  │  - tech_node / pressure_node / comprehensive_node│   │
│  │  - force_assessment / save_assessment            │   │
│  │  - Pydantic 评估校验 (validate_assessment)        │   │
│  └──────┬──────────────────────────────────────────┘   │
│         │                                               │
│  ┌──────▼──────────────────────────────────────────┐   │
│  │           Agent 层 (多智能体)                     │   │
│  │  - TechAgent / PressureAgent / ComprehensiveAgent│   │
│  │  - @retry(max_attempts=3, backoff=2.0)           │   │
│  │  - BaseAgent (JSON解析 / think标签过滤)           │   │
│  └──────┬──────────────────────────────────────────┘   │
│         │                                               │
│  ┌──────▼──────────────────────────────────────────┐   │
│  │           RAG 层 (ChromaDB)                       │   │
│  │  - RAGQuestionBank (三层去重管线)                 │   │
│  │  - RAGLogger (检索日志 + 性能日志)                │   │
│  │  - fetch_n动态扩窗 + 集合总量硬限保护              │   │
│  └──────┬──────────────────────────────────────────┘   │
│         │                                               │
│  ┌──────▼──────────────────────────────────────────┐   │
│  │           持久化层 (SQLite)                       │   │
│  │  - ProfileManager (JSON序列化)                   │   │
│  │  - _ensure_fields (字段兼容性)                    │   │
│  │  - 断点续考 (load/create_session)                │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 技术栈

### 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | >=0.104.0 | REST API 路由、异步处理、自动 OpenAPI 文档 |
| Uvicorn | >=0.24.0 | ASGI 服务器 |
| LangChain | >=0.1.0 | LLM 调用封装 |
| langchain-openai | >=0.0.5 | OpenAI 兼容模型调用 |
| Pydantic | >=2.0.0 | 状态契约、数据校验、AgentResponse 模型 |
| ChromaDB | >=0.4.0 | 向量数据库、面试题语义检索 |
| SQLite | 内置 | 会话状态持久化、断点续考 |
| PyPDF2 | >=3.0.0 | 简历 PDF 解析 |
| python-dotenv | >=1.0.0 | 环境变量加载 |

### 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4.21 | 前端框架、响应式 UI |
| TypeScript | ^5.4.5 | 类型安全 |
| Pinia | ^2.1.7 | 状态管理 |
| Vue Router | ^4.3.0 | 路由管理 |
| ECharts | ^5.5.0 | 能力雷达图可视化 |
| Axios | ^1.6.8 | HTTP 请求 |
| Tailwind CSS | ^3.4.3 | 原子化 CSS |
| Vite | ^5.2.8 | 构建工具 |

### 部署

| 技术 | 用途 |
|------|------|
| Docker | 容器化打包 |
| Docker Compose | 前后端服务编排、一键部署 |

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose（可选，用于容器化部署）

### 方式一：本地开发

#### 1. 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example ../.env
# 编辑 .env 文件，填入你的 API Key

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

后端服务启动后，访问 http://localhost:8000/docs 查看自动生成的 API 文档。

#### 2. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务启动后，访问 http://localhost:5173 开始使用。

### 方式二：Docker 一键部署

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 启动所有服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f
```

服务启动后：
- 后端 API：http://localhost:8000
- 前端界面：http://localhost:5173
- API 文档：http://localhost:8000/docs

---

## 项目结构

```
Interview-Colosseum/
├── backend/
│   ├── main.py                      # FastAPI 应用入口
│   ├── requirements.txt             # Python 依赖
│   ├── Dockerfile                   # 后端容器配置
│   ├── app/
│   │   ├── config.py                # 环境变量与配置
│   │   ├── core/
│   │   │   ├── orchestrator.py      # 核心编排器 (Pydantic状态 + 缓存管理)
│   │   │   ├── profile.py           # 会话持久化管理 (SQLite)
│   │   │   ├── nodes.py             # 节点函数 (直接调用，无LangGraph)
│   │   │   ├── assessment.py        # Pydantic评估Schema
│   │   │   └── evaluator.py         # 综合评估报告生成
│   │   ├── agents/
│   │   │   ├── base.py              # Agent基类 (JSON解析)
│   │   │   ├── tech.py              # 技术面Agent (@retry装饰器)
│   │   │   ├── pressure.py          # 压力面Agent (@retry装饰器)
│   │   │   └── comprehensive.py     # 综合面Agent (@retry装饰器)
│   │   ├── rag/
│   │   │   ├── question_bank.py     # RAG题库检索 (性能日志)
│   │   │   ├── rag_logger.py        # RAG日志工具
│   │   │   └── seed_data.py         # 种子题库
│   │   ├── routes/
│   │   │   └── interview.py         # FastAPI路由定义
│   │   └── utils/
│   │       ├── retry.py             # LLM重试装饰器
│   │       ├── db.py                # 数据库工具
│   │       └── resume.py            # 简历解析工具
├── frontend/
│   ├── src/
│   │   ├── api/index.ts             # API 请求封装
│   │   ├── components/
│   │   │   ├── ChatBubble.vue       # 对话气泡组件
│   │   │   ├── RadarChart.vue       # ECharts雷达图
│   │   │   └── StageIndicator.vue   # 阶段指示器
│   │   ├── store/interview.ts       # Pinia 状态管理
│   │   ├── types/index.ts           # TypeScript 类型定义
│   │   └── views/
│   │       ├── HomePage.vue         # 首页（简历上传）
│   │       ├── InterviewPage.vue    # 面试交互页
│   │       └── ReportPage.vue       # 评估报告页
│   ├── package.json
│   ├── Dockerfile
│   └── vite.config.ts
├── docker-compose.yml               # 服务编排
├── .env.example                     # 环境变量模板
└── .gitignore
```

---

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload-resume` | 上传简历文件（PDF） |
| POST | `/api/start-interview` | 开始面试（自动恢复活跃会话） |
| POST | `/api/interview-next` | 提交用户回答，获取下一题 |
| POST | `/api/skip-stage` | 跳过当前阶段 |
| POST | `/api/jump-to-final` | 跳过所有剩余阶段，直接进入最终评估 |
| POST | `/api/generate-report` | 生成综合评估报告 |
| POST | `/api/upload-questions` | 上传自定义题库 |
| GET | `/api/question-bank-stats` | 获取题库统计信息 |
| GET | `/health` | 健康检查 |

---

## 核心设计

### 面试流程

```
INIT → TECH (1-8轮) → PRESSURE (1-8轮) → COMPREHENSIVE (1-8轮) → DONE
  │         │                  │                    │
  │         ├─ skip_stage →    ├─ skip_stage →      ├─ skip_stage →
  │         │                  │                    │
  │         └─ jump_to_final ──────────────────────┘
```

### RAG 三层去重管线

```
query_questions(job_type, stage, k=2, asked_ids)
       │
       ▼
第一层：主过滤器
  ├─ ChromaDB where_filter = {"stage": stage, "job_type": job_type}
  ├─ fetch_n = min(max(k + len(asked_set), k*3, 5), collection_count)
  └─ 语义检索返回 fetch_n 条结果
       │
       ▼
第二层：内存Set精确去重
  ├─ asked_set = set(asked_ids)
  ├─ 遍历结果，过滤掉已在 asked_set 中的题目
  └─ 取前 k 条未问题目
       │
       ▼
第三层：Fallback二次去重
  ├─ 若过滤后为空，遍历 result_ids 找第一个不在 asked_set 中的题目
  └─ 若全部已问 → 返回 ["标准题库已耗尽，请基于简历自由追问"]
       │
       ▼
性能日志记录
  ├─ elapsed_ms (检索耗时)
  ├─ asked_count (已问题目数)
  └─ result_count (返回结果数)
```

### 断点续考机制

```
用户断网/刷新页面
       │
       ▼
Orchestrator.create_session(resume_id, job_type)
       │
       ├─ get_active_session_by_resume(resume_id) → 查询SQLite
       │
       ├─ 找到活跃会话 (stage != "DONE")
       │     ├─ 检查内存缓存 (TTL 1h)
       │     │     ├─ 未过期 → 直接返回
       │     │     └─ 已过期 → 从SQLite加载
       │     └─ 返回已有会话，继续面试
       │
       └─ 无活跃会话 → 创建新会话
```

### 评估加权算法

```
综合得分 = 技术深度 × 40% + 抗压能力 × 30% + 逻辑表达 × 15% + 诚信度 × 15%
```

---

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | LLM API Key | 必填 |
| `OPENAI_BASE_URL` | LLM API 地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `DEFAULT_MODEL` | 模型名称 | `qwen3.5-plus` |

---

## 架构演进

| 特性 | 重构前 | 重构后 |
|------|--------|--------|
| 状态机 | LangGraph (StateGraph + Conditional Edges) | 纯Python + Pydantic BaseModel |
| 状态契约 | TypedDict (弱类型) | Pydantic BaseModel (强类型校验) |
| 流程控制 | interview_graph.ainvoke() | 直接调用节点函数 (_run_node) |
| 评估校验 | 无 | Pydantic field_validator (分数范围+枚举值) |
| 缓存管理 | 普通 dict | OrderedDict + TTL + LRU淘汰 |
| LLM重试 | 无 | @retry装饰器 (指数退避) |
| 性能监控 | 无 | RAG检索性能日志 (elapsed_ms) |
| 依赖项 | langgraph + 其他 | 移除 langgraph，精简依赖 |

---

## 开发指南

### 添加新的面试阶段

1. 在 `app/agents/` 下创建新的 Agent 类，继承 `BaseAgent`
2. 在 `app/core/nodes.py` 中添加对应的节点函数
3. 在 `app/core/orchestrator.py` 的 `_NODE_MAP` 中注册节点
4. 在 `app/core/assessment.py` 中添加对应的 Pydantic 评估模型
5. 在 `STAGES` 列表中添加阶段名称

### 添加自定义题库

通过 API `POST /api/upload-questions` 上传 JSON 格式的题库：

```json
[
  {
    "id": "custom_001",
    "stage": "TECH",
    "category": "后端开发",
    "job_type": "Python",
    "question": "请解释 Python 的 GIL 是什么？",
    "reference_answer": "GIL（全局解释器锁）是..."
  }
]
```

---

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

---

## License

MIT License

---

## Star History

如果这个项目对你有帮助，请给它一个 ⭐️
