# MyAgent - 基于 DeepSeek 的 AI 命令行智能助手

MyAgent 是一个用 Python 编写的交互式命令行工具，集成 DeepSeek API 提供智能对话服务，并支持 **AI 控制 PowerShell 执行系统命令**。具备上下文管理、Token 消耗统计、自动对话压缩，以及 AI 驱动的命令执行功能。

## 🚀 新特性 (v2.0)

### AI 命令执行系统（**新增**）
- **结构化命令格式**: LLM 按照严格格式输出命令：
  - `reply:` - 直接回复用户
  - `command:` - 执行 PowerShell 命令（需用户确认）
  - `complete:` - 任务完成标记
  
- **交互式命令控制**: 每次执行前显示命令内容和解释，用户可选择 y/n 执行或拒绝
- **命令结果反馈**: AI 根据命令执行结果自动调整后续策略，支持连续操作
- **逐步执行**: 每次只执行一条命令，避免批量执行造成的不可控风险
- **用户干预机制**: 命令取消后用户可给出修改要求，AI 重新规划

### 原有特性维持
- **指令系统**: `agent` 前缀指令，支持 `init`, `tokens`, `zip`, `exit` 等操作
- **智能上下文管理**: 自动维护对话历史，支持手动压缩
- **Token 实时统计**: 监控 API 消耗，管理预算
- **系统提示词外部化**: 支持从 `Agent.md` 动态加载提示词，无需修改代码

## ⚠️ 免责声明

**本工具涉及直接执行系统命令，具有潜在风险。使用者必须理解以下事项：**

1. **风险承诺**: 
   - 用户对所有通过本工具执行的命令及其后果承担完全责任
   - 本工具不对以下情况负责：
     - 数据丢失、系统损坏、文件误删除
     - 系统崩溃、性能下降、权限提升后的恶意行为
     - 任何由 AI 生成的不安全命令导致的损害

2. **安全建议**:
   - ⚠️ **强烈建议在虚拟机或隔离环境中测试**
   - 每次执行命令前详细检查其内容和影响
   - 不要在生产系统上运行此工具
   - 定期备份重要数据
   - 使用受限权限的用户账户运行此工具（避免 Administrator/root 权限）

3. **AI 能力限制**:
   - DeepSeek 可能生成逻辑错误或危险的命令
   - 本工具不具有命令审核或白名单机制
   - LLM 幻觉可能导致生成不存在的命令或错误的语法

4. **免责条款**:
   本工具按"现状"提供，作者不提供任何明示或暗示的担保。使用者需自行承担所有风险。

**使用本工具即表示同意上述免责声明。**

---

## 🛠️ 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/AlvinLiu6/MyAgent.git
   cd MyAgent
   ```

2. **安装依赖**
   ```bash
   pip install openai python-dotenv
   ```

3. **配置环境**
   在项目根目录下创建 `.env` 文件：
   ```env
   OPENAI_API_KEY=your_deepseek_api_key_here
   USER_NAME=your_user_name_here
   ```

## 📖 使用指南

### 启动程序
```bash
python Agent.py
```

### 交互模式

#### 1. 普通对话
直接输入任何文字，AI 将正常回复：
```
>>>用户: 如何创建一个文本文件？
deepseek-reasoner: reply: 你可以使用 New-Item 命令来创建文本文件...
```

#### 2. AI 命令建议
AI 若建议执行命令，会按以下格式输出：
```
>>>用户: 帮我在这个文件夹下创建 a.txt，内容为 "test"
deepseek-reasoner: 对执行此命令的解释

[待执行命令] New-Item -ItemType File -Path a.txt -Value "test"
是否执行此命令? (y/n): 
```

**用户选择**:
- `y` - 执行命令，AI 显示结果并继续操作
- `n` - 取消执行，可输入修改要求，AI 重新规划

#### 3. 管理指令
在任何时候输入 `agent` 前缀指令：

| 指令 | 描述 |
| :--- | :--- |
| `agent help` | 显示帮助手册 |
| `agent tokens` | 查看 Token 消耗统计 |
| `agent zip` | 压缩对话历史，保留核心上下文 |
| `agent init`/`clear` | 重置对话，清空上下文 |
| `agent quit`/`exit` | 安全退出程序 |

### 输出格式规范

**v2.0 中不同的 AI 回复格式有不同含义，用户需要理解：**

| 格式 | 含义 | 示例 | 用户操作 |
| :--- | :--- | :--- | :--- |
| `reply:` | 纯文本回复，不执行命令 | `reply: 这是一个 PowerShell 教程...` | 阅读回复 |
| `command:` | 建议执行命令 | `command: Get-Process --explain: 查询进程` | 选择 y/n |
| `complete:` | 任务已完成 | `complete: 已为你创建了 a.txt 文件` | 确认完成 |

## 🏗️ 核心架构

```
Agent.py
├── load_system_prompt()     # 从 Agent.md 加载系统提示词
├── ChatContext              # 对话上下文管理
├── execute_powershell_command()  # PowerShell 命令执行器
├── parse_and_process_response()  # AI 回复解析器（新增）
└── main loop                # 交互循环
```

### 关键设计

1. **外部提示词**: `Agent.md` 定义 LLM 输出规范，便于修改而无需改代码
2. **命令验证**: 每次执行前显示命令，用户可决定是否执行
3. **结果反馈**: 命令结果实时反馈给 LLM，支持后续操作链
4. **错误恢复**: 取消后支持修改要求，AI 重新规划任务

## 📝 配置说明

### Agent.md（系统提示词）
定义 LLM 输出格式和行为约束：
- 三种回复格式的详细说明
- CRITICAL 规则：禁止混合格式
- 执行约束：一次一条命令，等待反馈

修改此文件可以**不重启程序**地改变 AI 行为（仅对新启动的程序有效）。

### 环境变量
- `OPENAI_API_KEY`: DeepSeek API 密钥（必需）

## 📊 使用案例

### 案例 1：创建文件并写入内容
```
>>>用户: 在这个文件夹下生成 a.txt，写入 "Hello World"
deepseek-reasoner: 这个任务很简单。我会为你创建文件。

[待执行命令] New-Item -ItemType File -Path a.txt -Value "Hello World"
是否执行此命令? (y/n): y

[执行中...]
Powershell: 

    Directory: C:\code\program\MyAgent

Mode                 LastWriteTime         Length Name
----                 -----------         ------ ----
-a---          2025-03-18 10:30:00              11 a.txt

complete: 文件已创建并成功写入内容。
```

### 案例 2：查询进程
```
>>>用户: 帮我查一下有没有 notepad 进程
deepseek-reasoner: 我会帮你查询 notepad 进程。

[待执行命令] Get-Process -Name notepad -ErrorAction SilentlyContinue | Select-Object Name,ID
是否执行此命令? (y/n): y

[执行中...]
Powershell: 
Name     ID
----     --
notepad  1234

complete: 找到 1 个 notepad 进程，进程 ID 为 1234。
```

## 🎯 性能指标

- **启动时间**: < 1 秒（加载系统提示词）
- **API 响应**: 2-10 秒（取决于网络和模型推理）
- **命令执行**: < 5 秒（大多数系统命令）

## 🔍 故障排查

| 问题 | 原因 | 解决方案 |
| :--- | :--- | :--- |
| `找不到 Agent.md` | 工作目录错误 | 确保在项目根目录运行 `python Agent.py` |
| `OPENAI_API_KEY not found` | 未配置 .env 文件 | 创建 `.env` 并填入有效的 API Key |
| 命令执行失败 | PowerShell 版本或权限问题 | 使用 PowerShell 5.1+，或使用管理员权限 |
| 中文输出乱码 | 编码问题 | 检查 `.env` 环境变量的编码为 UTF-8 |

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request。主要改进方向：
- [ ] 命令白名单审核
- [ ] 更智能的风险提示
- [ ] 支持更多系统平台（macOS、Linux）
- [ ] Web UI 界面


**最后提醒: 在您同意免责声明并充分理解风险后，方可使用本工具。**
