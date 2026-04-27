# CLAUDE.md - 项目开发规范

## 项目概述

**项目名称**: new_graph_chat_export (AI旅行助手)
**项目类型**: 基于 LangGraph 的多智能体旅行客服系统
**技术栈**: FastAPI + LangGraph + Python

## 核心功能

- ✈️ **航班服务**: 查询、改签、取消航班
- 🏨 **酒店服务**: 搜索、预订、修改、取消酒店
- 🚗 **租车服务**: 搜索、预订、修改、取消租车
- 🎯 **景点推荐**: 智能推荐旅游景点
- 🌐 **网络搜索**: 获取最新信息

## 架构说明

### 多智能体架构

```
supervisor (主管Agent)
├── research_agent (网络搜索)
├── flight_booking_agent (航班)
├── hotel_booking_agent (酒店)
├── car_rental_booking_agent (租车)
└── excursion_booking_agent (景点推荐)
```

### 目录结构

```
new_graph_chat_export/
├── main.py                     # FastAPI 入口
├── requirements.txt            # Python 依赖
├── new_graph_chat/             # 核心工作流
│   ├── graph.py                # 工作流定义
│   ├── all_agent.py            # Agent 定义
│   ├── state.py                # 状态管理
│   ├── my_llm.py               # LLM 配置
│   └── checkpoint_config.py   # Checkpointer 配置
├── tools/                      # 业务工具
├── api/                        # API 层
├── config/                     # 配置
├── utils/                      # 工具函数
└── db/                         # 数据库
```

### 关键文件

| 文件 | 说明 |
|------|------|
| `new_graph_chat/graph.py` | LangGraph 工作流定义 |
| `new_graph_chat/all_agent.py` | 6个 Agent 的定义 |
| `tools/*.py` | 业务工具实现 |
| `api/graph_api/new_graph_views.py` | API 接口 |
| `main.py` | FastAPI 应用入口 |

## 最近优化 (2026-04-25)

### 1. 多轮对话优化
- **问题**: 子 agent 执行完后直接 END，导致多轮对话上下文丢失
- **解决**: 修改工作流，子 agent 执行完后返回 supervisor，由 supervisor 总结输出
- **修改文件**: `new_graph_chat/graph.py`, `new_graph_chat/all_agent.py`

### 2. 酒店位置搜索优化
- **问题**: 搜索"外滩"等区域时无法找到附近酒店
- **解决**: 修改搜索逻辑，同时匹配位置字段和酒店名称字段
- **修改文件**: `tools/hotels_tools.py`

### 3. 网络搜索修复
- **问题**: 智谱AI API 配额用尽导致搜索失败
- **解决**: 用户充值后恢复使用
- **修改文件**: `tools/net_search_tool.py`

### 4. Streamlit 测试界面
- **功能**: 添加纯白色简洁风格的测试界面
- **启动**: `streamlit run app.py --server.port 8502`
- **地址**: http://localhost:8502

## 最近优化 (2026-04-27)

### 1. 后端路由修复
- **问题**: `api/routers.py` 引用了不存在的模块 (deep_agent_views)
- **解决**: 更新路由配置，使用现有的 new_graph_views
- **修改文件**: `api/routers.py`

### 2. 缺失文件创建
- **问题**: 缺少用户管理相关文件，导致启动失败
- **解决**: 创建了 api/system_mgt/user_schemas.py、user_views.py
- **修改文件**: `api/system_mgt/*.py`

### 3. 配置文件修复
- **问题**: 配置文件缺失 (development.yml)，导致配置项加载失败
- **解决**: 修改 config/__init__.py，从 .env 加载配置并设置默认值
- **修改文件**: `config/__init__.py`, `config/log_config.py`

### 4. 编码问题修复
- **问题**: Windows 环境下 print 输出 emoji 字符时报编码错误
- **解决**: 在 my_print.py 中强制设置 UTF-8 编码
- **修改文件**: `new_graph_chat/my_print.py`

### 5. bcrypt 兼容性修复
- **问题**: passlib 与 bcrypt 5.0.0 不兼容
- **解决**: 降级 bcrypt 到 4.3.0
- **修改命令**: `pip install "bcrypt<5.0.0"`

### 6. 前端构建配置
- **问题**: 前端缺少构建配置文件，无法启动
- **解决**: 创建 static/package.json、static/vite.config.js
- **启动命令**: `cd static && npm install && npm run build`

### 7. 登录接口修复
- **问题**: 前端发送 JSON 格式，后端只支持 OAuth2 表单格式
- **解决**: 修改登录接口支持 JSON 格式
- **修改文件**: `api/system_mgt/user_views.py`

### 8. 删除前端代码
- **原因**: 准备重写前端
- **删除内容**: 移除 static/ 目录和 main.py 中的静态文件相关代码
- **注意**: API 接口保持不变，可供新前端调用

## API 接口文档

### 基础配置
- Base URL: `http://localhost:8000`
- Content-Type: `application/json`

### 用户接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/register/` | 用户注册 |
| POST | `/api/login/` | 用户登录 |
| GET | `/api/profile/` | 获取当前用户信息（需认证） |

### 工作流接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/new_graph/` | 同步调用工作流 |
| POST | `/api/new_graph/stream/` | 流式调用工作流 |

### 请求示例

**用户注册**:
```json
POST /api/register/
{
  "username": "testuser",
  "password": "test123456",
  "phone": "13800138000",
  "real_name": "张三"
}
```

**用户登录**:
```json
POST /api/login/
{
  "username": "testuser",
  "password": "test123456"
}
```

**调用工作流**:
```json
POST /api/new_graph/
{
  "user_input": "帮我查一下明天上海到北京的航班"
}
```

**响应**:
```json
{
  "assistant": "您好！根据您的需求...",
  "interrupted": false,
  "error": null
}
```

## 开发规范

### 限制条件

#### 1. 文档同步更新
> **每次优化完代码后，必须同步更新 CLAUDE.md**

- 添加新功能模块时，同步更新"核心功能"和"关键文件"
- 修改架构时，同步更新"架构说明"
- 添加新的工具或 API 时，同步更新目录结构

#### 2. 功能模块修改规范
> **每次修改功能模块，必须进行测试和 Code Review**

- 单元测试: 验证核心函数的正确性
- 集成测试: 验证 API 接口正常工作
- Code Review: 检查代码质量、安全性、可维护性

#### 3. 问题排查流程
> **每次测试时遇到问题，都按照以下流程进行记录**

```
发现问题 → 如何排查 → 排查结果 → 解决方案 → 解决后的结果
```

问题记录模板:
```markdown
## 问题记录

### 问题描述
[清晰描述遇到的问题]

### 发现时间
YYYY-MM-DD

### 如何排查
1. [排查步骤1]
2. [排查步骤2]
3. [排查步骤3]

### 排查结果
[分析得出的根本原因]

### 解决方案
[具体的修复方案]

### 解决后的结果
[修复后的验证结果]
```

### 代码规范

1. **命名规范**: 使用有意义的英文命名，遵循 Python 命名约定
2. **注释规范**: 不添加明显代码的注释，只添加 WHY 非显式的说明
3. **函数规范**: 单一职责，函数长度控制在合理范围内
4. **错误处理**: 在系统边界添加适当的错误处理和日志

### 环境配置

- Python 3.11+
- 虚拟环境: `.venv/`
- 必需环境变量 (`.env`):
  - `DEEPSEEK_API_KEY`: DeepSeek API 密钥
  - `ZHIPU_API_KEY`: 智谱AI API 密钥

### 开发规范

#### 端口资源管理
> **每次测试完成后，必须释放端口资源**

- 使用后台运行服务时，测试完成后使用 `TaskStop` 停止任务
- 避免端口占用导致下次启动失败
- Windows 上可以使用 `netstat -ano | findstr :8000` 查看端口占用

#### 2. 代码提交规范
> **每次修改代码后，必须提交到 GitHub**

- 使用 git 提交所有修改的文件
- 提交信息要清晰描述本次修改的内容
- 禁止直接 push 到 main 分支，应创建 feature 分支或使用 PR

```bash
# 激活虚拟环境
source .venv/Scripts/activate  # Windows
# source .venv/bin/activate    # Linux/Mac

# 启动服务
python main.py

# API 文档: http://localhost:8000/docs
```

## 待办事项

- [x] 配置开发环境
- [x] 理解现有代码结构
- [x] 运行基础测试
- [x] 优化多轮对话（子agent返回supervisor总结）
- [x] 修复酒店位置搜索问题

## 未来优化计划（待考虑）

### 多轮对话性能优化 (方案C)

**背景**: 当前方案（子 agent 返回 supervisor 总结）会增加 1-2 秒延迟和 token 消耗

**方案C: 利用 LangGraph 状态管理优化**

通过 State 传递结果，避免重复调用 LLM：

1. 在 `state.py` 中添加 `agent_result` 字段存储子 agent 结果
2. 在 `graph.py` 中使用 Command 传递结果
3. Supervisor 直接读取并转发，不需要再次调用 LLM

**预期效果**:
- 消除额外 LLM 调用，响应更快
- 降低 token 消耗成本

**待修改文件**:
- `new_graph_chat/state.py`
- `new_graph_chat/graph.py`
- `new_graph_chat/all_agent.py`