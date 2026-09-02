"""工具的定义与执行。

一个 Agent 的差异化就在于它手里有工具。
本文件分两部分：
1. TOOL_SCHEMAS：把工具描述成 JSON Schema，告诉大模型"你有这些工具可用"
2. execute_tool：真正执行工具的 Python 函数
"""

import datetime
import json

from rag import search_knowledge


# 待办清单的"状态"存在这里，模拟数据库
TODO_LIST = []


# 工具清单：大模型会根据用户的话，自己决定要不要调、调哪个
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，例如：1+2*3、sqrt(16)、(8+2)/5",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "获取当前的日期和时间",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "在本地知识库中检索资料，用于回答用户提出的、需要参考资料的问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户问题的关键词"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_todo",
            "description": "把一件事记进待办清单",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "待办事项的内容"
                    }
                },
                "required": ["text"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_todos",
            "description": "查看当前待办清单里有什么",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]


def execute_tool(name: str, arguments: str) -> str:
    """根据工具名调用对应实现，返回结果字符串。"""
    args = json.loads(arguments) if arguments else {}

    if name == "calculate":
        # 用 eval 做计算是教学 Demo 的简化写法，生产环境要限制表达式
        expr = args["expression"]
        return str(eval(expr))

    if name == "get_time":
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if name == "search_knowledge":
        return search_knowledge(args["query"])

    if name == "add_todo":
        text = args["text"]
        TODO_LIST.append(text)
        return f"已添加：{text}，当前共 {len(TODO_LIST)} 条待办"

    if name == "list_todos":
        if not TODO_LIST:
            return "待办清单是空的"
        return "\n".join(f"{i + 1}. {t}" for i, t in enumerate(TODO_LIST))

    return f"未知工具：{name}"
