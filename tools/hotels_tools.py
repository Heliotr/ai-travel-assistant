"""
酒店相关工具模块
提供酒店搜索、预订、更新和取消等功能
"""

from sqlite3 import connect
from datetime import date, datetime
from typing import Optional, Union

from langchain_core.tools import tool

from tools import db
from tools.location_trans import get_all_variants


@tool
def search_hotels(
        location: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = 10,
) -> list[dict]:
    """
    搜索酒店

    根据位置和名称搜索酒店，支持中英文匹配和区域搜索。
    - 支持按城市搜索：如 "上海"
    - 支持按区域/商圈搜索：如 "外滩"、"陆家嘴"、"西湖"
    - 支持按酒店名称搜索
    默认返回10条结果，避免返回过多数据。

    参数:
        location: 酒店位置（城市名/区域名/商圈名）
        name: 酒店名称关键词
        limit: 返回结果数量限制，默认10条
    """
    conn = connect(db)
    conn.text_factory = str
    cursor = conn.cursor()

    # 获取中英文变体
    location_variants = get_all_variants(location)
    query = "SELECT * FROM hotels WHERE 1=1"
    params = []

    if location_variants:
        # 方案1: 匹配位置字段
        conditions = " OR ".join(["location LIKE ?" for _ in location_variants])
        # 方案2: 匹配酒店名称（支持区域/商圈搜索，如"外滩"、"西湖"）
        name_conditions = " OR ".join(["name LIKE ?" for _ in location_variants])
        query += f" AND (({conditions}) OR ({name_conditions}))"
        params.extend([f"%{v}%" for v in location_variants])
        params.extend([f"%{v}%" for v in location_variants])

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    # 添加排序和限制
    query += " ORDER BY id LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()

    # 获取总数量（用于告知用户）
    count_query = query.replace("ORDER BY id LIMIT ?", "")
    count_params = params[:-1]
    cursor.execute(count_query, count_params)
    total_count = len(cursor.fetchall())

    conn.close()

    # 压缩结果，只返回关键信息
    compressed_results = []
    for row in results:
        full_dict = dict(zip([column[0] for column in cursor.description], row))
        # 只保留关键信息
        compressed_results.append({
            'id': full_dict.get('id'),
            'name': full_dict.get('name', '')[:30],  # 限制名称长度
            'location': full_dict.get('location'),
            'price_tier': full_dict.get('price_tier'),
            'checkin_date': full_dict.get('checkin_date'),
            'checkout_date': full_dict.get('checkout_date'),
            'booked': full_dict.get('booked'),
        })

    # 如果结果被截断，添加提示
    if total_count > limit:
        compressed_results.append({
            '_meta': f"共找到 {total_count} 条结果，仅显示前 {limit} 条"
        })

    return compressed_results


@tool
def book_hotel(hotel_id: int) -> str:
    """
    预订酒店

    根据酒店ID标记为已预订
    """
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute("UPDATE hotels SET booked = 1 WHERE id = ?", (hotel_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"酒店 {hotel_id} 成功预订。"
    else:
        conn.close()
        return f"未找到ID为 {hotel_id} 的酒店。"


@tool
def update_hotel(
        hotel_id: int,
        checkin_date: Optional[Union[datetime, date]] = None,
        checkout_date: Optional[Union[datetime, date]] = None,
) -> str:
    """
    更新酒店预订

    修改酒店的入住和退房日期
    """
    conn = connect(db)
    cursor = conn.cursor()

    if checkin_date:
        cursor.execute(
            "UPDATE hotels SET checkin_date = ? WHERE id = ?", (checkin_date, hotel_id)
        )
    if checkout_date:
        cursor.execute(
            "UPDATE hotels SET checkout_date = ? WHERE id = ?", (checkout_date, hotel_id)
        )

    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"酒店 {hotel_id} 成功更新。"
    else:
        conn.close()
        return f"未找到ID为 {hotel_id} 的酒店。"


@tool
def cancel_hotel(hotel_id: int) -> str:
    """
    取消酒店预订

    将酒店预订状态标记为未预订
    """
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute("UPDATE hotels SET booked = 0 WHERE id = ?", (hotel_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"酒店 {hotel_id} 已取消。"
    else:
        conn.close()
        return f"未找到ID为 {hotel_id} 的酒店。"