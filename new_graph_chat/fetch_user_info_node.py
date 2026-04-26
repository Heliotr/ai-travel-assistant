from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import MessagesState

from new_graph_chat.state import State
from tools.flights_tools import fetch_user_flight_information
import sqlite3
from pathlib import Path


def get_user_flight_data(passenger_id: str):
    """直接查询数据库获取用户航班信息（不经过工具）"""
    db_path = Path(__file__).parent.parent / "travel_new.sqlite"
    if not db_path.exists():
        return None

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    query = """
    SELECT
        t.ticket_no, t.book_ref,
        f.flight_id, f.flight_no, f.departure_airport, f.arrival_airport, f.scheduled_departure, f.scheduled_arrival,
        bp.seat_no, tf.fare_conditions
    FROM
        tickets t
        JOIN ticket_flights tf ON t.ticket_no = tf.ticket_no
        JOIN flights f ON tf.flight_id = f.flight_id
        JOIN boarding_passes bp ON bp.ticket_no = t.ticket_no AND bp.flight_id = f.flight_id
    WHERE
        t.passenger_id = ?
    """
    cursor.execute(query, (passenger_id,))
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]
    results = [dict(zip(column_names, row)) for row in rows]

    cursor.close()
    conn.close()

    return results if results else None


def get_user_info(state: State, config: RunnableConfig):
    """
    获取用户的航班信息并存储在状态中。
    注意：这个信息不会直接显示给用户，而是供后续agent使用。

    参数:
        state (State): 当前状态字典。
        config (RunnableConfig): 运行配置，包含 passenger_id
    返回:
        dict: 包含用户信息的状态（不作为消息显示给用户）
    """
    # 检查是否已有用户信息，如果有则跳过查询（避免每次都查询）
    existing_user_info = state.get('user_info')
    if existing_user_info:
        # 已有用户信息，不再重复查询
        return None

    # 从 config 中获取 passenger_id，而不是硬编码
    configurable = config.get('configurable', {}) if config else {}
    passenger_id = configurable.get('passenger_id')

    if not passenger_id:
        # 没有 passenger_id，不查询用户信息
        return {"user_info": None}

    try:
        # 直接查询数据库，不经过工具（避免工具结果被添加到消息历史）
        flight_data = get_user_flight_data(passenger_id)

        if flight_data:
            # 只将用户信息存储在 state 中，不作为消息返回给用户
            return {
                "user_info": str(flight_data)
            }
        else:
            return {
                "user_info": None
            }
    except Exception as e:
        # 查询失败时静默处理
        return {"user_info": None}