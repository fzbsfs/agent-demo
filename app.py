"""Streamlit 网页界面：给 Agent 套一个能点、能看的壳。

启动方式：streamlit run app.py
"""

import streamlit as st

from agent import Agent


st.set_page_config(page_title="我的第一个 Agent", page_icon="🤖")


@st.cache_resource
def get_agent():
    """全局只创建一次 Agent，保留会话记忆。"""
    return Agent(system_prompt="你是一个乐于助人的助理。回答用户问题前，"
                               "需要工具就先用工具。")


st.title("我的第一个 Agent")
st.caption("会算数、会看时间、会查本地知识库的小助理")

agent = get_agent()

if agent.use_mock:
    st.warning("当前是演示模式，还没连接真实大模型。"
               "在 config.py 里填好 API Key 后会自动切换到真实模式。")

# 初始化聊天记录
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 显示历史消息
for role, text in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(text)

# 输入框
if prompt := st.chat_input("跟我说点什么，比如：帮我算 1+2*3"):
    st.session_state.chat_history.append(("user", prompt))
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Agent 正在思考..."):
            reply = agent.chat(prompt)
        st.write(reply)
    st.session_state.chat_history.append(("assistant", reply))
