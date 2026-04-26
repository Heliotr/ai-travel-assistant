# 贡献指南

感谢你对 AI 旅行助手项目的关注！欢迎参与贡献。

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 在 [Issues](https://github.com/Heliotr/ai-travel-assistant/issues) 中搜索是否已有相关问题
2. 如果没有，创建新的 Issue，详细描述问题或建议

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/your-username/ai-travel-assistant.git
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **编写代码**
   - 遵循项目代码规范
   - 添加必要的测试
   - 更新相关文档

4. **提交更改**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **创建 Pull Request**
   - 描述你的更改内容
   - 关联相关的 Issue

## 代码规范

### Python 代码

- 使用有意义的变量和函数命名
- 遵循 PEP 8 规范
- 只在必要时添加注释（说明 WHY，不是 WHAT）
- 函数保持单一职责

### 提交信息格式

```
<type>: <subject>

<body>
```

类型：
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建/工具相关

## 开发环境设置

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API 密钥

# 运行测试
python -m pytest

# 启动服务
python main.py
```

## 行为准则

- 尊重所有贡献者
- 保持建设性的讨论
- 欢迎不同观点和经验水平