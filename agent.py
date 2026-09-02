"""Agent 核心：调用大模型 + 工具调度的循环。

这是整个 Demo 的灵魂，面试时讲清楚这一段就够了：

1. 把用户的输入放进会话历史
2. 把整段历史 + 工具清单发给大模型
3. 大模型要么直接回答，要么说"我要调用工具 X"
4. 如果它想调用工具：我们执行工具，把结果塞回会话，回到第 2 步
5. 直到大模型直接回答，返回给用户

这个"思考 -> 行动 -> 观察结果 -> 再思考"的循环，就是 Agent。

没填 API Key 时会自动进入演示模式（_mock_chat），
用规则模拟同样的循环，方便先看懂结构。
"""

import json
import re

from openai import OpenAI

from config import API_KEY, BASE_URL, MODEL, is_mock_mode
from tools import TOOL_SCHEMAS, execute_tool


# 防止死循环：最多让大模型连续调用这么多轮工具，再多就兜底停
MAX_TOOL_ROUNDS = 5


class Agent:
    def __init__(self, system_prompt: str):
        self.model = MODEL
        # messages 就是 Agent 的"记忆"：多轮对话 + 工具执行结果都记在这里
        self.messages = [{"role": "system", "content": system_prompt}]
        self.use_mock = is_mock_mode()
        if self.use_mock:
            self.client = None
        else:
            self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    def chat(self, user_input: str) -> str:
        """接收用户一句话，走完 Agent 循环，返回最终回答。"""
        if self.use_mock:
            return self._mock_chat(user_input)

        self.messages.append({"role": "user", "content": user_input})

        # 循环直到大模型给出最终回答；限制轮数，防止死循环
        for _ in range(MAX_TOOL_ROUNDS + 1):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=TOOL_SCHEMAS,
            )
            message = response.choices[0].message

            # 情况一：大模型想调用工具
            if message.tool_calls:
                # 先把"它想调用工具"这件事记入历史
                self.messages.append(message)
                for tool_call in message.tool_calls:
                    name = tool_call.function.name
                    arguments = tool_call.function.arguments
                    try:
                        result = execute_tool(name, arguments)
                    except Exception as exc:
                        # 把错误记回历史，大模型看到后能换个策略
                        result = f"工具执行出错：{type(exc).__name__}: {exc}，请换个方式处理"
                    # 再把"工具返回的结果"记入历史，大模型才能基于结果作答
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    })
                continue  # 带着工具结果，重新问大模型

            # 情况二：大模型直接回答，返回结果
            self.messages.append(message)
            return message.content or "(空回答)"

        # 轮数耗尽还没答完，兜底
        return "工具调用次数太多，已停止，请换个问法。"

    def _mock_chat(self, user_input: str) -> str:
        """演示模式：用关键词规则模拟大模型的工具决策。

        这只是在没 Key 时用来展示循环骨架的，真实模式里
        "该不该调工具、调哪个"是由大模型决定的。
        """
        steps = [f"[思考] 用户说：{user_input}"]
        tool_name, tool_args = None, {}

        if "记" in user_input or "添加" in user_input or "记录" in user_input:
            text = user_input
            for word in ["帮我记一下", "记一下", "帮我记", "添加", "记录一下", "记录"]:
                if text.startswith(word):
                    text = text[len(word):].strip()
                    break
            tool_name, tool_args = "add_todo", {"text": text}
        elif "待办" in user_input or "清单" in user_input:
            tool_name, tool_args = "list_todos", {}
        elif "时间" in user_input or "日期" in user_input or "几点" in user_input:
            tool_name, tool_args = "get_time", {}
        elif "算" in user_input or "+" in user_input or "-" in user_input or "*" in user_input:
            # 从整句话里抠出数学表达式，只留数字和运算符
            expr = re.sub(r"[^\d+\-*/()., ]", "", user_input).strip()
            tool_name, tool_args = "calculate", {"expression": expr}
        elif "RAG" in user_input or "知识" in user_input or "Agent" in user_input:
            tool_name, tool_args = "search_knowledge", {"query": user_input}

        if tool_name:
            steps.append(f"[行动] 调用工具 {tool_name}，参数 {tool_args}")
            try:
                result = execute_tool(tool_name, json.dumps(tool_args, ensure_ascii=False))
            except Exception as exc:
                # 演示模式同样兜住异常，不会让程序崩溃
                result = f"工具执行出错：{type(exc).__name__}: {exc}"
            steps.append(f"[观察] 工具返回：{result}")
            steps.append(f"[回答] {result}")
        else:
            steps.append("[回答] 演示模式：这句我没接真实大模型，"
                         "填好 API Key 后才能真正对话。")
        return "\n\n".join(steps)
