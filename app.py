"""
Streamlit 旅行助手测试界面
简洁白色风格，类似豆包、DeepSeek 等 AI 应用
"""
import streamlit as st
import uuid
import time
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="AI旅行助手",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 引入工作流
from new_graph_chat.graph import execute_graph, execute_graph_stream, create_session_config

# 初始化会话状态
if 'session_config' not in st.session_state:
    st.session_state.session_config = create_session_config()

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_agent' not in st.session_state:
    st.session_state.current_agent = None

if 'is_streaming' not in st.session_state:
    st.session_state.is_streaming = False


def send_message(user_input: str):
    """发送消息并获取回复（同步方式）"""
    st.session_state.is_streaming = True

    # 添加用户消息
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    # 执行工作流（使用同步方式）
    config = st.session_state.session_config
    full_response = ""
    agent_name = "旅行助手"

    # 使用流式获取
    try:
        for event in execute_graph_stream(user_input, config):
            if event['type'] == 'agent':
                agent_name = event.get('agent', '旅行助手')
                st.session_state.current_agent = agent_name

            elif event['type'] == 'content':
                content = event.get('content', '')
                full_response += content

            elif event['type'] == 'end':
                break

    except Exception as e:
        full_response = f"抱歉，发生了错误：{str(e)}"

    # 添加助手消息
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "agent": agent_name,
        "timestamp": datetime.now().strftime("%H:%M")
    })

    st.session_state.is_streaming = False


def clear_chat():
    """清空对话"""
    st.session_state.messages = []
    st.session_state.current_agent = None
    st.session_state.session_config = create_session_config()


# 自定义 CSS - 纯白色简洁风格
st.markdown("""
<style>
    /* 全局样式 */
    .stApp {
        background: #ffffff;
    }

    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 主容器 */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
        min-height: 100vh;
    }

    /* 顶部标题 */
    .header {
        text-align: center;
        padding: 20px 0 40px;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 30px;
    }

    .header h1 {
        font-size: 28px;
        font-weight: 600;
        color: #333;
        margin: 0;
    }

    .header p {
        font-size: 14px;
        color: #999;
        margin: 8px 0 0;
    }

    /* 消息样式 */
    .message {
        display: flex;
        gap: 12px;
        margin-bottom: 24px;
        animation: fadeIn 0.3s ease;
    }

    .message.user {
        flex-direction: row-reverse;
    }

    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }

    .message.user .message-avatar {
        background: #007AFF;
        color: white;
    }

    .message.assistant .message-avatar {
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
    }

    .message-content {
        max-width: 70%;
        padding: 14px 18px;
        border-radius: 16px;
        font-size: 15px;
        line-height: 1.6;
        word-wrap: break-word;
    }

    .message.user .message-content {
        background: #007AFF;
        color: white;
        border-bottom-right-radius: 4px;
    }

    .message.assistant .message-content {
        background: #f8f9fa;
        color: #333;
        border: 1px solid #f0f0f0;
        border-bottom-left-radius: 4px;
    }

    .message-time {
        font-size: 11px;
        color: #bbb;
        margin-top: 4px;
    }

    .message.user .message-time {
        text-align: right;
    }

    /* Agent 标签 */
    .agent-tag {
        display: inline-block;
        padding: 2px 8px;
        background: #e8f4ff;
        color: #007AFF;
        border-radius: 4px;
        font-size: 12px;
        margin-bottom: 6px;
    }

    /* 输入区域 */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        border-top: 1px solid #f0f0f0;
        padding: 16px 20px;
        z-index: 100;
    }

    .input-wrapper {
        max-width: 800px;
        margin: 0 auto;
        display: flex;
        gap: 12px;
        align-items: flex-end;
    }

    .stTextInput > div > div > input {
        padding: 14px 18px !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 24px !important;
        font-size: 15px !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #007AFF !important;
        box-shadow: none !important;
    }

    .stButton > button {
        padding: 14px 28px !important;
        background: #007AFF !important;
        color: white !important;
        border: none !important;
        border-radius: 24px !important;
        font-size: 15px !important;
    }

    .stButton > button:hover {
        background: #0066dd !important;
    }

    .stButton > button:disabled {
        background: #ccc !important;
    }

    /* 清空按钮 */
    .clear-btn {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 8px 16px;
        background: white;
        color: #666;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        font-size: 13px;
        cursor: pointer;
        transition: all 0.2s;
        z-index: 100;
    }

    .clear-btn:hover {
        background: #f5f5f5;
        border-color: #ccc;
    }

    /* 快捷输入按钮 */
    .quick-inputs {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        justify-content: center;
        margin-top: 20px;
        padding: 0 20px;
    }

    .quick-input {
        padding: 8px 16px;
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 20px;
        font-size: 13px;
        color: #666;
        cursor: pointer;
        transition: all 0.2s;
    }

    .quick-input:hover {
        background: #e8f4ff;
        border-color: #007AFF;
        color: #007AFF;
    }

    /* 欢迎语 */
    .welcome {
        text-align: center;
        padding: 60px 20px;
    }

    .welcome h2 {
        font-size: 24px;
        font-weight: 500;
        color: #333;
        margin-bottom: 16px;
    }

    .welcome p {
        font-size: 14px;
        color: #999;
        margin-bottom: 30px;
    }

    /* 动画 */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* 滚动条 */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: transparent;
    }

    ::-webkit-scrollbar-thumb {
        background: #ddd;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #ccc;
    }

    /* 底部占位 */
    .bottom-placeholder {
        height: 100px;
    }

    /* 加载动画 */
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 10px 0;
    }

    .typing-indicator span {
        width: 8px;
        height: 8px;
        background: #007AFF;
        border-radius: 50%;
        animation: typing 1.4s infinite;
    }

    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }

    @keyframes typing {
        0%, 60%, 100% {
            transform: translateY(0);
        }
        30% {
            transform: translateY(-10px);
        }
    }
</style>
""", unsafe_allow_html=True)


# 页面布局
st.markdown('<div class="header"><h1>✈️ AI旅行助手</h1><p>基于 LangGraph 多智能体架构的旅行客服系统</p></div>', unsafe_allow_html=True)

# 清空对话按钮
if st.button("🗑️ 清空对话", key="clear_btn"):
    clear_chat()
    st.rerun()

# 快捷输入按钮（使用 HTML 按钮触发 JavaScript）
st.markdown("""
<div class="quick-inputs">
    <button class="quick-input" onclick="setQuickInput('查询明天上海到北京的航班')">✈️ 航班查询</button>
    <button class="quick-input" onclick="setQuickInput('帮我预订上海外滩附近的三星级酒店')">🏨 酒店预订</button>
    <button class="quick-input" onclick="setQuickInput('我要租一辆商务车')">🚗 租车服务</button>
    <button class="quick-input" onclick="setQuickInput('推荐杭州西湖附近的景点')">🎯 景点推荐</button>
</div>

<script>
function setQuickInput(text) {
    const input = document.querySelector('input[type="text"]');
    if (input) {
        input.value = text;
        input.focus();
    }
}
</script>
""", unsafe_allow_html=True)

st.markdown("---")

# 显示聊天消息
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <h2>您好！我是旅行助手</h2>
        <p>我可以帮您查询航班、预订酒店、租车服务、推荐景点</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="message user">
                <div class="message-avatar">👤</div>
                <div>
                    <div class="message-content">{msg["content"]}</div>
                    <div class="message-time">{msg["timestamp"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            agent = msg.get("agent", "旅行助手")
            agent_emoji = {
                "supervisor": "👨‍💼",
                "flight_booking_agent": "✈️",
                "hotel_booking_agent": "🏨",
                "car_rental_booking_agent": "🚗",
                "excursion_booking_agent": "🎯",
                "research_agent": "🔍"
            }.get(agent, "🤖")

            st.markdown(f"""
            <div class="message assistant">
                <div class="message-avatar">{agent_emoji}</div>
                <div>
                    <span class="agent-tag">{agent}</span>
                    <div class="message-content">{msg["content"]}</div>
                    <div class="message-time">{msg["timestamp"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 底部占位
st.markdown('<div class="bottom-placeholder"></div>', unsafe_allow_html=True)

# 输入区域
user_input = st.text_input(
    label=" ",
    placeholder="请输入您的问题...",
    label_visibility="collapsed",
    key="user_input"
)

# 发送按钮
if st.button("发送", key="send_btn", disabled=st.session_state.is_streaming):
    if user_input.strip():
        send_message(user_input.strip())
        st.rerun()