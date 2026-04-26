"""
Checkpointer 配置模块
统一管理 LangGraph 的持久化配置
"""
import os
from pathlib import Path
from langgraph.checkpoint.memory import InMemorySaver


def get_checkpointer():
    """
    根据环境变量选择持久化方式
    - memory: 内存存储（开发/测试，快速）
    - sqlite: SQLite文件存储（生产环境，暂不推荐）
    """
    checkpoint_type = os.getenv('CHECKPOINT_TYPE', 'memory')  # 默认为内存

    if checkpoint_type == 'memory':
        print("[Checkpointer] 使用内存存储 (InMemorySaver)")
        return InMemorySaver()
    elif checkpoint_type == 'sqlite':
        from langgraph.checkpoint.sqlite import SqliteSaver
        basic_dir = Path(__file__).resolve().parent.parent
        db_path = os.getenv('CHECKPOINT_DB_PATH', str(basic_dir / "checkpoints.db"))
        print(f"[Checkpointer] 使用 SQLite 存储: {db_path}")
        # 使用 SQLite 连接字符串
        return SqliteSaver.from_conn_string(f"sqlite:///{db_path}")
    else:
        raise ValueError(f"不支持的 CHECKPOINT_TYPE: {checkpoint_type}")


# 创建全局 checkpointer 实例
checkpointer = get_checkpointer()