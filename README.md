# AI旅行助手 - 多智能体旅行客服系统

基于 LangGraph 的多智能体旅行客服系统，提供航班、酒店、租车、景点推荐等一站式旅行服务。

## 功能特性

- ✈️ **航班服务**: 查询、改签、取消航班
- 🏨 **酒店服务**: 搜索、预订、修改、取消酒店
- 🚗 **租车服务**: 搜索、预订、修改、取消租车
- 🎯 **景点推荐**: 智能推荐旅游景点
- 🌐 **网络搜索**: 获取最新实时信息
- 💬 **多轮对话**: 支持上下文连续对话

## 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| AI框架 | LangGraph, LangChain |
| LLM | DeepSeek / OpenAI / 智谱AI |
| 前端 | Vue 3 |
| 数据库 | SQLite / MySQL |
| 测试界面 | Streamlit |

## 系统架构

```
supervisor (主管Agent)
├── research_agent (网络搜索)
├── flight_booking_agent (航班服务)
├── hotel_booking_agent (酒店服务)
├── car_rental_booking_agent (租车服务)
└── excursion_booking_agent (景点推荐)
```

主管 Agent 负责理解用户意图，将任务分发给对应的专业子 Agent，并整合结果返回给用户。

## 目录结构

```
new_graph_chat_export/
├── main.py                     # FastAPI 入口
├── app.py                      # Streamlit 测试界面
├── requirements.txt            # Python 依赖
├── .env.example                # 环境变量模板
│
├── new_graph_chat/             # 核心工作流
│   ├── graph.py                # 工作流定义
│   ├── all_agent.py            # Agent 定义
│   ├── state.py                # 状态管理
│   └── my_llm.py               # LLM 配置
│
├── tools/                      # 业务工具
│   ├── flights_tools.py        # 航班工具
│   ├── hotels_tools.py         # 酒店工具
│   ├── car_tools.py            # 租车工具
│   └── trip_tools.py           # 景点工具
│
├── api/                        # API 层
│   └── graph_api/              # 工作流接口
│
├── config/                     # 配置
├── utils/                      # 工具函数
├── db/                         # 数据库
└── static/src/                 # 前端 (Vue 3)
```

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Heliotr/ai-travel-assistant.git
cd ai-travel-assistant
```

### 2. 创建虚拟环境

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API 密钥
# 必须配置: DEEPSEEK_API_KEY 或 OPENAI_API_KEY
```

### 5. 启动服务

```bash
# 启动 FastAPI 服务
python main.py

# 或启动 Streamlit 测试界面
streamlit run app.py --server.port 8502
```

### 访问地址

- **API 文档**: http://localhost:8000/docs
- **Streamlit 界面**: http://localhost:8502

## API 接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/new_graph/stream/` | POST | 流式调用 (SSE) |
| `/api/new_graph/` | POST | 同步调用 |
| `/health` | GET | 健康检查 |

### 请求示例

```bash
# 同步调用
curl -X POST "http://localhost:8000/api/new_graph/" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "帮我查询北京到上海的航班"}]}'
```

## 环境变量说明

| 变量名 | 说明 | 必填 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 二选一 |
| `OPENAI_API_KEY` | OpenAI API 密钥 | 二选一 |
| `ZHIPU_API_KEY` | 智谱 AI API 密钥 (网络搜索) | 否 |
| `DATABASE_URL` | 数据库连接字符串 | 否 |

## 项目亮点

- **多智能体协同**: 基于 LangGraph 的层级式多智能体架构
- **专业分工**: 每个 Agent 专注于特定领域，提高任务处理精度
- **多轮对话**: 子 Agent 执行后返回 supervisor 总结，保持上下文连续
- **灵活扩展**: 易于添加新的 Agent 和工具

## 开发路线

- [x] 多智能体架构设计
- [x] 航班/酒店/租车/景点四大服务
- [x] 多轮对话优化
- [x] FastAPI + Streamlit 双界面
- [ ] 多轮对话性能优化 (利用状态管理减少 LLM 调用)
- [ ] 用户认证与权限管理
- [ ] 部署与 Docker 支持

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件