"""
新工作流主模块
基于 LangGraph 多智能体架构
支持敏感操作中断、多种持久化方式、SSE 流式响应
"""

import os
import uuid
from pathlib import Path
from typing import Generator, Optional

from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.types import Command

from new_graph_chat.checkpoint_config import checkpointer, get_checkpointer  # 统一配置
from new_graph_chat.all_agent import (
    supervisor_agent,
    research_agent,
    flight_booking_agent,
    hotel_booking_agent,
    car_rental_booking_agent,
    excursion_booking_agent,
)
from new_graph_chat.draw_png import draw_graph
from new_graph_chat.fetch_user_info_node import get_user_info
from new_graph_chat.my_print import pretty_print_messages
from new_graph_chat.state import State
from tools.init_db import update_dates


# ============ 持久化配置（已迁移到 checkpoint_config.py） ============
# 通过 checkpoint_config 导入统一的 checkpointer

# ============ 工作流图定义 ============
# 子 agent 执行完后返回 supervisor，由 supervisor 总结输出
builder = (
    StateGraph(State)
    # 添加所有节点
    .add_node('fetch_user_info', get_user_info)  # 获取用户信息存到 state
    .add_node('supervisor', supervisor_agent)
    .add_node('research_agent', research_agent)
    .add_node('flight_booking_agent', flight_booking_agent)
    .add_node('hotel_booking_agent', hotel_booking_agent)
    .add_node('car_rental_booking_agent', car_rental_booking_agent)
    .add_node('excursion_booking_agent', excursion_booking_agent)
    # 添加边
    .add_edge(START, 'fetch_user_info')
    .add_edge('fetch_user_info', 'supervisor')  # 获取用户信息后交给 supervisor

    # 子 agent 执行完后返回 supervisor，由 supervisor 总结输出
    .add_edge('research_agent', 'supervisor')
    .add_edge('flight_booking_agent', 'supervisor')
    .add_edge('hotel_booking_agent', 'supervisor')
    .add_edge('car_rental_booking_agent', 'supervisor')
    .add_edge('excursion_booking_agent', 'supervisor')

    .add_edge('supervisor', END)
)

# 编译工作流（暂不使用 interrupt_before，因为 create_react_agent 内部处理）
graph = builder.compile(checkpointer=checkpointer)


# ============ 会话配置 ============
def create_session_config(passenger_id: str = "3442 587242") -> dict:
    """
    创建新的会话配置

    参数:
        passenger_id: 乘客ID，默认为测试用户

    返回:
        包含 configurable 的配置字典
    """
    session_id = str(uuid.uuid4())
    return {
        "configurable": {
            "passenger_id": passenger_id,
            "thread_id": session_id,
        }
    }


# ============ 响应提取 ============
def extract_ai_response(state) -> str:
    """
    从状态中提取 AI 的最后回复

    参数:
        state: StateSnapshot 或状态字典

    返回:
        AI 回复的文本内容
    """
    # StateSnapshot 对象有 values 属性，是一个字典
    if hasattr(state, 'values'):
        messages = state.values.get('messages', [])
    else:
        messages = state.get('messages', []) if isinstance(state, dict) else []

    for msg in reversed(messages):
        # 找到最后一个 AI 消息
        if hasattr(msg, 'type') and msg.type == 'ai':
            content = msg.content
            if content and isinstance(content, str) and content.strip():
                return content.strip()
        elif hasattr(msg, 'name') and msg.name in [
            'supervisor',
            'research_agent',
            'flight_booking_agent',
            'hotel_booking_agent',
            'car_rental_booking_agent',
            'excursion_booking_agent'
        ]:
            # 来自 Agent 的消息
            content = msg.content
            if content and isinstance(content, str) and content.strip():
                return content.strip()
    return ""


# ============ 同步执行函数 ============
def execute_graph(user_input: str, config: dict = None) -> dict:
    """
    执行工作流的函数（同步方式）

    参数:
        user_input: 用户输入
        config: 会话配置

    返回字典包含:
        - response: AI 回复内容
        - tool_calls: 工具调用列表
        - interrupted: 是否需要用户确认
        - error: 错误信息 (如果有)
    """
    result = {
        'response': '',
        'tool_calls': [],
        'interrupted': False,
        'error': None
    }

    try:
        current_state = graph.get_state(config)
        if current_state.next:  # 出现了工作流的中断
            human_command = Command(resume={'answer': user_input})
            for chunk in graph.stream(human_command, config, stream_mode='values'):
                pretty_print_messages(chunk, last_message=True)
        else:
            for chunk in graph.stream({'messages': ('user', user_input)}, config):
                pretty_print_messages(chunk, last_message=True)

        # 获取最终状态
        final_state = graph.get_state(config)

        # 检查是否中断（需要用户确认）
        if final_state.next:
            result['interrupted'] = True
            if final_state.interrupts:
                # StateSnapshot.interrupts[0] 是 Interrupt 对象，有 value 属性
                interrupt = final_state.interrupts[0]
                result['response'] = getattr(interrupt, 'value', '请确认是否继续')

        # 提取 AI 响应
        result['response'] = extract_ai_response(final_state)

    except Exception as e:
        result['error'] = str(e)
        result['response'] = f"发生错误: {str(e)}"

    return result


# ============ 流式执行函数 ============
def execute_graph_stream(user_input: str, config: dict) -> Generator[dict, None, None]:
    """
    流式执行工作流，返回事件流
    类似于旧工作流的 SSE 接口

    参数:
        user_input: 用户输入
        config: 会话配置

    Yields:
        事件字典，包含 type 字段
    """
    try:
        current_state = graph.get_state(config)

        # 如果有中断，处理用户确认
        if current_state and current_state.next:
            human_command = Command(resume={'answer': user_input})
            for chunk in graph.stream(human_command, config, stream_mode='values'):
                messages = chunk.get('messages', [])
                for msg in messages:
                    if hasattr(msg, 'type') and msg.type == 'ai':
                        yield {'type': 'agent', 'agent': getattr(msg, 'name', 'unknown')}
                        if msg.content:
                            yield {'type': 'content', 'content': msg.content, 'agent': getattr(msg, 'name', 'unknown')}
                    elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            yield {'type': 'tool', 'tool': tc.get('name', 'unknown')}
                    elif hasattr(msg, 'name') and hasattr(msg, 'content'):
                        yield {'type': 'tool_result', 'tool': msg.name, 'content': str(msg.content)[:200]}

        else:
            # 正常流式处理
            last_agent = None
            for chunk in graph.stream({'messages': ('user', user_input)}, config, stream_mode='values'):
                messages = chunk.get('messages', [])
                if messages:
                    for msg in messages:
                        # AI 消息
                        if hasattr(msg, 'type') and msg.type == 'ai':
                            agent_name = getattr(msg, 'name', 'unknown')
                            if agent_name != last_agent:
                                last_agent = agent_name
                                yield {'type': 'agent', 'agent': agent_name}
                            if msg.content:
                                yield {'type': 'content', 'content': msg.content, 'agent': agent_name}
                            else:
                                yield {'type': 'content', 'content': '', 'agent': agent_name}
                        # 工具调用
                        elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tc in msg.tool_calls:
                                yield {'type': 'tool', 'tool': tc.get('name', 'unknown')}
                        # 工具返回结果
                        elif hasattr(msg, 'name') and hasattr(msg, 'content'):
                            content = str(msg.content)[:200] if msg.content else ''
                            yield {'type': 'tool_result', 'tool': msg.name, 'content': content}

        # 检查是否需要确认
        final_state = graph.get_state(config)
        if final_state and final_state.next:
            yield {'type': 'confirm', 'content': 'AI助手即将执行上述操作，您是否批准？输入 "y" 继续，或输入您的修改要求。'}
        else:
            yield {'type': 'end'}

    except Exception as e:
        yield {'type': 'error', 'message': str(e)}


# ============ 测试函数 ============
def test_workflow():
    """测试新工作流"""
    import sys

    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 60)
    print("新工作流测试")
    print("=" * 60)

    # 创建会话配置
    config = create_session_config()
    print(f"会话配置: {config}")

    # 测试问题列表
    test_questions = [
        "你好",
        "帮我查一下明天从北京到上海的航班",
        "我想预订一家酒店",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n[{i}] 用户: {question}")
        try:
            result = execute_graph(question, config)
            if result.get('error'):
                print(f"    [X] 错误: {result['error']}")
            else:
                response = result.get('response', '')
                preview = response[:100].replace("\n", " ") if len(response) > 100 else response
                print(f"    AI: {preview}...")
                if result.get('interrupted'):
                    print(f"    [!] 需要用户确认")
        except Exception as e:
            print(f"    [X] 错误: {str(e)[:80]}")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_workflow()
