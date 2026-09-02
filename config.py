import os

# API 配置：默认接 DeepSeek（兼容 OpenAI 协议）
# 也可以改成其他厂商：换 BASE_URL 和 MODEL 即可
API_KEY = os.getenv("AGENT_API_KEY", "在这里填你的Key")
BASE_URL = os.getenv("AGENT_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.getenv("AGENT_MODEL", "deepseek-chat")


def is_mock_mode() -> bool:
    """还没填 Key 时自动进入演示模式。

    演示模式不调真实大模型，用规则模拟"思考->调用工具->回答"的循环，
    方便在没 Key、没网络的情况下先看懂 Agent 长什么样。
    """
    return API_KEY == "" or API_KEY.startswith("在这里")
