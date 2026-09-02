# Agent Demo：会调用工具、会检索知识库的智能助手

一个**从零手写**的 Agent，用最少的代码讲清楚大模型应用的核心：
工具调用（Function Calling）、RAG 检索、跨轮记忆、错误处理。

## 亮点

- 手写 Agent 循环：思考 -> 调用工具 -> 观察结果 -> 再回答
- Function Calling：计算、时间、待办等真实工具，JSON Schema 描述
- 最简版 RAG：词频向量 + 余弦相似度检索本地知识库
- 错误处理：try/except 捕获工具异常、错误回传模型换策略、调用轮数上限防死循环
- 无 Key 演示模式：不填 API Key 也能跑通完整流程
- Streamlit 界面 + 命令行演示脚本，方便现场展示

## 技术栈

Python · OpenAI SDK · Function Calling · RAG · Streamlit

## 演示

（此处放演示录屏或截图，建议录一段：算数 -> 查时间 -> 查知识库 -> 记待办）

真实对话需要 DeepSeek API Key，见下方"怎么跑"。

## 怎么跑

1. 安装依赖

```bash
python -m pip install -r requirements.txt
```

2. 启动（不填 Key 也能跑，会自动进入演示模式）

```bash
streamlit run app.py
```

3. 要连接真实大模型，在 `config.py` 里把 `在这里填你的Key`
换成 DeepSeek 的 API Key（或设置环境变量 `AGENT_API_KEY`），
重启后自动切换到真实模式。

演示模式下输入「现在几点」「帮我算 1+2*3」「什么是RAG」
「记一下明天交作业」能看到完整的思考 -> 调用工具 -> 回答流程。

想快速排练，可以跑命令行演示脚本（不依赖浏览器）：

```bash
python demo_script.py          # 演示模式
python demo_script.py --real   # 真实模式（需已填 Key）
```

## 面试要点

重点看 [docs/interview-guide.md](docs/interview-guide.md)，
里面写了 30 秒开场白、现场演示话术、每个文件怎么讲、
以及高频追问 TOP 10 的标准回答。

求职材料：
- [docs/resume-and-self-intro.md](docs/resume-and-self-intro.md)：简历项目描述 + 自我介绍话术
- [docs/algorithm-plan.md](docs/algorithm-plan.md)：4 周算法补课计划（高频题 + 模板）

## 演示点

- 输入「现在几点了」→ 触发 `get_time` 工具
- 输入「帮我算 (8+2)/5」→ 触发 `calculate` 工具
- 输入「什么是 RAG」→ 触发 `search_knowledge` 检索本地知识库
- 输入「记一下明天交作业」再问「待办清单」→ 展示跨轮记忆和有状态工具

## 文件说明

| 文件 | 作用 |
|------|------|
| `agent.py` | Agent 核心循环（思考 -> 调用工具 -> 观察结果）+ 演示模式 |
| `tools.py` | 工具定义（JSON Schema）与执行 |
| `rag.py` | 最简版检索增强生成 |
| `config.py` | API 配置 |
| `app.py` | Streamlit 界面 |
| `demo_script.py` | 面试演示排练器（命令行一键跑所有功能点） |
| `knowledge/` | 本地知识库，放 .md 文件即可 |
| `docs/interview-guide.md` | 面试讲解稿（怎么讲、答什么） |
| `docs/resume-and-self-intro.md` | 简历描述与自我介绍 |
| `docs/algorithm-plan.md` | 算法补课计划 |
