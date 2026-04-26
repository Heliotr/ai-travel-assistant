"""
工具节点处理器模块
提供工具节点创建和错误处理功能
"""

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.prebuilt import ToolNode


def handle_tool_error(state) -> dict:
    """
    工具错误处理函数
    当工具执行失败时，生成错误消息返回给用户

    参数:
        state: 包含错误信息和消息列表的状态字典

    返回:
        包含错误信息的ToolMessage列表
    """
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"错误: {repr(error)}\n请修正您的错误。",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }


def create_tool_node_with_fallback(tools: list) -> dict:
    """
    创建带回退机制的工具节点

    参数:
        tools: 工具列表

    返回:
        带有错误处理回退的工具节点
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)],
        exception_key="error"
    )


def _print_event(event: dict, _printed: set, max_length=1500):
    """
    打印事件信息，用于调试

    参数:
        event: 事件字典
        _printed: 已打印消息集合
        max_length: 消息最大长度
    """
    current_state = event.get("dialog_state")
    if current_state:
        print("当前处于: ", current_state[-1])
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... （已截断）"
            print(msg_repr)
            _printed.add(message.id)