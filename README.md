# MyAgent - 基于 DeepSeek 的轻量级命令行助手

MyAgent 是一个用 Python 编写的交互式命令行工具，旨在通过 DeepSeek API 提供智能对话服务。它具备上下文管理、Token 消耗统计以及自动对话压缩功能。

## 🚀 新特性 (v1.1)

- **指令系统**: 引入 `agent` 前缀指令，支持 `init`, `tokens`, `zip`, `exit` 等操作。
- **智能上下文管理**: 自动维护对话历史，支持手动触发对话压缩以节省 Token。
- **Token 实时统计**: 监控每一次交互的消耗，帮助你掌控 API 预算。
- **增强稳定性**: 修复了角色混淆 bug，并引入了更健壮的输入解析机制。

## 🛠️ 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/AlvinLiu6/MyAgent.git
   ```

2. **安装依赖**
   本项目依赖 `openai` 和 `python-dotenv` 库：
   ```bash
   pip install openai python-dotenv
   ```

3. **配置环境**
   在项目根目录下创建一个 `.env` 文件，并填入你的 API Key：
   ```env
   OPENAI_API_KEY=your_deepseek_api_key_here
   ```

## 📖 使用指南

直接运行脚本即可进入对话模式：
```bash
python Agent.py
```

### 交互指令

在对话框中输入 `agent` 加以下子命令即可执行管理操作：

| 指令 | 描述 |
| :--- | :--- |
| `agent help` | 显示帮助手册 |
| `agent tokens` | 查看当前会话累计消耗的 Token 量 |
| `agent zip` | 压缩并总结当前对话历史，保留核心上下文 |
| `agent init` | 重置对话，清空所有上下文记忆 |
| `agent exit` | 安全退出程序并显示最终统计信息 |

### 普通对话
直接输入任何文字，AI 将根据当前的上下文回复你。

## 🏗️ 核心架构

项目采用 **Context-Driven (上下文驱动)** 模式：
- **ChatContext 类**: 封装了消息列表、模型设置和 Token 计数器。
- **命令分发器**: 利用 Python 字典实现轻量级路由，方便未来扩展新功能。
- **DeepSeek Reasoner**: 默认使用逻辑推理能力强大的 `deepseek-reasoner` 模型。

## ⚠️ 注意事项

- 请确保你的 DeepSeek 账户余额充足。
- 本程序默认开启了 `thinking` 模式（针对推理模型），请根据具体的 API 供应商文档调整 `extra_body` 参数。
