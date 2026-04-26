"""
航班相关工具模块
提供航班搜索、用户航班信息查询、机票改签和取消等功能
"""

from sqlite3 import connect
from datetime import date, datetime
from typing import Optional, List, Dict
import pytz
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from tools import db


@tool
def fetch_user_flight_information(config: RunnableConfig) -> List[Dict]:
    """
    获取用户机票信息

    通过乘客ID查询该乘客的所有机票信息，
    包括航班详情和座位分配情况
    """
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("未配置乘客ID。")

    conn = connect(db)
    cursor = conn.cursor()

    # SQL查询：连接多个表获取完整信息
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

    return results


@tool
def search_flights(
        departure_airport: Optional[str] = None,
        arrival_airport: Optional[str] = None,
        start_time: Optional[date | datetime] = None,
        end_time: Optional[date | datetime] = None,
        limit: int = 10,
) -> List[Dict]:
    """
    搜索航班

    根据出发地、目的地和时间范围搜索航班。
    支持机场代码（如PEK、PVG）或城市名（如北京、上海）。
    默认返回10条结果，避免返回过多数据。

    参数:
        departure_airport: 出发机场或城市
        arrival_airport: 到达机场或城市
        start_time: 出发时间起始
        end_time: 出发时间结束
        limit: 返回结果数量限制，默认10条
    """
    conn = connect(db)
    cursor = conn.cursor()

    # 如果提供的是城市名，需要先查找对应的机场代码
    departure_airport_codes = None
    arrival_airport_codes = None

    if departure_airport:
        # 尝试查找机场代码
        cursor.execute(
            "SELECT airport_code FROM airports_data WHERE airport_code = ? OR city LIKE ?",
            (departure_airport, f'%{departure_airport}%')
        )
        codes = [row[0] for row in cursor.fetchall()]
        if codes:
            departure_airport_codes = codes

    if arrival_airport:
        # 尝试查找机场代码
        cursor.execute(
            "SELECT airport_code FROM airports_data WHERE airport_code = ? OR city LIKE ?",
            (arrival_airport, f'%{arrival_airport}%')
        )
        codes = [row[0] for row in cursor.fetchall()]
        if codes:
            arrival_airport_codes = codes

    query = "SELECT * FROM flights WHERE 1 = 1"
    params = []

    if departure_airport_codes:
        placeholders = ','.join(['?'] * len(departure_airport_codes))
        query += f" AND departure_airport IN ({placeholders})"
        params.extend(departure_airport_codes)
    elif departure_airport:
        # 没找到城市对应的机场，直接用原始值
        query += " AND departure_airport = ?"
        params.append(departure_airport)

    if arrival_airport_codes:
        placeholders = ','.join(['?'] * len(arrival_airport_codes))
        query += f" AND arrival_airport IN ({placeholders})"
        params.extend(arrival_airport_codes)
    elif arrival_airport:
        query += " AND arrival_airport = ?"
        params.append(arrival_airport)

    if start_time:
        query += " AND scheduled_departure >= ?"
        params.append(start_time)

    if end_time:
        query += " AND scheduled_departure <= ?"
        params.append(end_time)

    query += " ORDER BY scheduled_departure LIMIT ?"
    params.append(limit)
    cursor.execute(query, params)
    rows = cursor.fetchall()
    column_names = [column[0] for column in cursor.description]

    # 压缩结果，只返回关键信息
    compressed_results = []
    for row in rows:
        full_dict = dict(zip(column_names, row))
        # 只保留关键信息
        compressed_results.append({
            'flight_id': full_dict.get('flight_id'),
            'flight_no': full_dict.get('flight_no'),
            'departure_airport': full_dict.get('departure_airport'),
            'arrival_airport': full_dict.get('arrival_airport'),
            'scheduled_departure': full_dict.get('scheduled_departure'),
            'scheduled_arrival': full_dict.get('scheduled_arrival'),
            'status': full_dict.get('status'),
        })

    cursor.close()
    conn.close()

    return compressed_results


@tool
def update_ticket_to_new_flight(
        ticket_no: str, new_flight_id: int, *, config: RunnableConfig
) -> str:
    """
    改签机票

    将用户机票更新为新的航班，会验证：
    1. 乘客ID是否存在
    2. 新航班ID是否有效
    3. 起飞时间距离当前时间是否大于3小时
    4. 原机票是否存在
    5. 乘客是否是机票持有者
    """
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("未配置乘客ID。")

    conn = connect(db)
    cursor = conn.cursor()

    # 查询新航班信息
    cursor.execute(
        "SELECT departure_airport, arrival_airport, scheduled_departure FROM flights WHERE flight_id = ?",
        (new_flight_id,),
    )
    new_flight = cursor.fetchone()
    if not new_flight:
        cursor.close()
        conn.close()
        return "提供的新的航班ID无效。"

    column_names = [column[0] for column in cursor.description]
    new_flight_dict = dict(zip(column_names, new_flight))

    # 验证：新航班起飞时间距离当前时间需大于3小时
    timezone = pytz.timezone("Etc/GMT-3")
    current_time = datetime.now(tz=timezone)
    departure_time = datetime.strptime(
        new_flight_dict["scheduled_departure"], "%Y-%m-%d %H:%M:%S.%f%z"
    )
    time_until = (departure_time - current_time).total_seconds()
    if time_until < (3 * 3600):
        return f"不允许重新安排到距离当前时间少于3小时的航班。"

    # 验证原机票存在
    cursor.execute(
        "SELECT flight_id FROM ticket_flights WHERE ticket_no = ?", (ticket_no,)
    )
    current_flight = cursor.fetchone()
    if not current_flight:
        cursor.close()
        conn.close()
        return "未找到给定机票号码的现有机票。"

    # 验证乘客身份
    cursor.execute(
        "SELECT * FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
        (ticket_no, passenger_id),
    )
    current_ticket = cursor.fetchone()
    if not current_ticket:
        cursor.close()
        conn.close()
        return f"当前登录的乘客不是机票{ticket_no}的拥有者。"

    # 更新机票
    cursor.execute(
        "UPDATE ticket_flights SET flight_id = ? WHERE ticket_no = ?",
        (new_flight_id, ticket_no),
    )
    conn.commit()

    cursor.close()
    conn.close()
    return "机票已成功更新为新的航班。"


@tool
def cancel_ticket(ticket_no: str, *, config: RunnableConfig) -> str:
    """
    取消机票

    验证乘客身份后，从数据库删除机票记录
    """
    configuration = config.get("configurable", {})
    passenger_id = configuration.get("passenger_id", None)
    if not passenger_id:
        raise ValueError("未配置乘客ID。")

    conn = connect(db)
    cursor = conn.cursor()

    # 验证机票存在
    cursor.execute(
        "SELECT flight_id FROM ticket_flights WHERE ticket_no = ?", (ticket_no,)
    )
    existing_ticket = cursor.fetchone()
    if not existing_ticket:
        cursor.close()
        conn.close()
        return "未找到给定机票号码的现有机票。"

    # 验证乘客身份
    cursor.execute(
        "SELECT flight_id FROM tickets WHERE ticket_no = ? AND passenger_id = ?",
        (ticket_no, passenger_id),
    )
    current_ticket = cursor.fetchone()
    if not current_ticket:
        cursor.close()
        conn.close()
        return f"当前登录的乘客不是机票{ticket_no}的拥有者。"

    # 删除机票
    cursor.execute("DELETE FROM ticket_flights WHERE ticket_no = ?", (ticket_no,))
    conn.commit()

    cursor.close()
    conn.close()
    return "机票已成功取消。"