import sys
import io
from typing import List, Sequence

from langchain_core.messages import convert_to_messages, BaseMessage

# 强制设置标准输出编码为 UTF-8
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass


def _safe_print(*args, **kwargs):
    """安全的打印函数，处理编码问题"""
    try:
        print(*args, **kwargs)
    except (UnicodeEncodeError, AttributeError):
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)


def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        _safe_print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    _safe_print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        _safe_print(f"Update from subgraph {graph_id}:")
        _safe_print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        _safe_print(update_label)
        _safe_print("\n")

        if not node_update:
            continue
        if 'messages' not in node_update:
            if isinstance(node_update, Sequence) and isinstance(node_update[-1], BaseMessage):
                pretty_print_message(node_update[-1])
            else:
                _safe_print(node_update)
            _safe_print("--------------\n")
            continue
        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        _safe_print("\n")