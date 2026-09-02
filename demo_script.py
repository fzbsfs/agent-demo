"""面试演示排练器。

跑法：
  演示模式（不连真实模型）：python demo_script.py
  真实模式（需要已填 Key）：python demo_script.py --real

作用：自动按顺序跑完所有功能点，方便你面试前反复排练话术。
"""

import argparse
import sys

from agent import Agent
from config import is_mock_mode


# 演示清单：每项 =（演示话术，要展示的功能点）
DEMO_CASES = [
    ("帮我算 (8+2)/5", "计算器工具"),
    ("现在几点了", "查时间工具"),
    ("什么是RAG", "知识库检索（RAG）"),
    ("记一下明天交作业", "写待办（有状态工具）"),
    ("待办清单", "读待办（跨轮记忆）"),
]


def main():
    parser = argparse.ArgumentParser(description="Agent 面试演示排练器")
    parser.add_argument("--real", action="store_true", help="走真实大模型（需已填 Key）")
    args = parser.parse_args()

    if args.real and is_mock_mode():
        print("请先在 config.py 填好 API Key，再用 --real 走真实模式")
        sys.exit(1)

    agent = Agent(system_prompt="你是乐于助人的助理，需要工具就先调用工具。")
    mode = "真实模型" if not agent.use_mock else "演示模式"
    print(f"当前模式：{mode}")
    print("=" * 40)

    for index, (question, point) in enumerate(DEMO_CASES, 1):
        print(f"\n==== 演示点 {index}：{point} ====")
        print(f"用户：{question}")
        print(agent.chat(question))


if __name__ == "__main__":
    main()
