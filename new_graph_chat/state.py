# 状态类
from typing import TypedDict, Annotated, Optional, Literal

from langchain_core.messages import AnyMessage, RemoveMessage
from langgraph.graph import add_messages


# 消息窗口大小配置
MAX_MESSAGE_TURNS = 10  # 保留最近 10 轮对话 (1轮 = 用户消息 + AI响应)


def add_messages_with_window(left: list[AnyMessage], right: AnyMessage | list[AnyMessage] | list[RemoveMessage]) -> list[AnyMessage]:
    """
    带消息窗口的消息添加函数

    在添加新消息后，自动裁剪超过窗口大小的旧消息。
    保留最近 MAX_MESSAGE_TURNS 轮对话。

    参数:
        left: 当前的消息列表
        right: 新消息或删除指令

    返回:
        更新后的消息列表（限制在窗口大小内）
    """
    # 先使用标准的 add_messages 处理
    messages = add_messages(left, right)

    # 如果是删除操作，直接返回
    if isinstance(right, list) and all(isinstance(m, RemoveMessage) for m in right):
        return messages

    # 计算需要保留的消息数量
    # 每轮对话包含：用户消息 + AI响应(可能有工具调用)
    # 保守策略：保留最近 MAX_MESSAGE_TURNS * 3 条消息 (考虑工具调用/结果)
    max_messages = MAX_MESSAGE_TURNS * 3

    if len(messages) > max_messages:
        # 保留最近的 max_messages 条消息
        messages = messages[-max_messages:]

    return messages


def update_dialog_stack(left: list[str], right: Optional[str]) -> list[str]:
    """
    更新对话状态栈

    参数:
        left: 当前的状态栈
        right: 新状态动作
            - None: 不做任何更改
            - "pop": 弹出栈顶元素
            - 其他: 添加到栈顶

    返回:
        更新后的状态栈
    """
    if right is None:
        return left
    if right == "pop":
        return left[:-1]
    return left + [right]


class State(TypedDict):
    """
    定义一个结构化的字典类型，用于存储对话状态信息。
    字段:
        messages (list[AnyMessage]): 使用 Annotated 注解附加了 add_messages_with_window 功能的消息列表，
                                     自动裁剪超出窗口大小的旧消息，防止 token 超限。
        user_info (str): 存储用户信息的字符串。
        dialog_state (list[Literal[...]]): 对话状态栈，管理多轮对话中的状态
    """
    messages: Annotated[list[AnyMessage], add_messages_with_window]
    user_info: str
    dialog_state: Annotated[
        list[Literal[
            "assistant",
            "update_flight",
            "book_car_rental",
            "book_hotel",
            "book_excursion",
        ]],
        update_dialog_stack,
    ]