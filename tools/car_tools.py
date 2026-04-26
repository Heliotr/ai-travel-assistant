"""
租车相关工具模块
提供租车搜索、预订、更新和取消等功能
"""

from sqlite3 import connect
from datetime import date, datetime
from typing import Optional, Union

from langchain_core.tools import tool

from tools import db
from tools.location_trans import get_all_variants


@tool
def search_car_rentals(
        location: Optional[str] = None,
        name: Optional[str] = None,
        limit: int = 10,
) -> list[dict]:
    """
    搜索租车服务

    根据位置和公司名称搜索租车选项，支持中英文匹配。
    默认返回10条结果，避免返回过多数据。

    参数:
        location: 租车地点
        name: 租车公司名称关键词
        limit: 返回结果数量限制，默认10条
    """
    conn = connect(db)
    cursor = conn.cursor()

    # 获取中英文变体
    location_variants = get_all_variants(location)
    query = "SELECT * FROM car_rentals WHERE 1=1"
    params = []

    if location_variants:
        conditions = " OR ".join(["location LIKE ?" for _ in location_variants])
        query += f" AND ({conditions})"
        params.extend([f"%{v}%" for v in location_variants])

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    query += " ORDER BY id LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()

    # 压缩结果
    compressed_results = []
    for row in results:
        full_dict = dict(zip([column[0] for column in cursor.description], row))
        compressed_results.append({
            'id': full_dict.get('id'),
            'name': full_dict.get('name', '')[:30],
            'location': full_dict.get('location'),
            'price_tier': full_dict.get('price_tier'),
            'start_date': full_dict.get('start_date'),
            'end_date': full_dict.get('end_date'),
            'booked': full_dict.get('booked'),
        })

    return compressed_results


@tool
def book_car_rental(rental_id: int) -> str:
    """
    预订租车

    根据租车ID标记为已预订
    """
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute("UPDATE car_rentals SET booked = 1 WHERE id = ?", (rental_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"租车 {rental_id} 成功预订。"
    else:
        conn.close()
        return f"未找到ID为 {rental_id} 的租车服务。"


@tool
def update_car_rental(
        rental_id: int,
        start_date: Optional[Union[datetime, date]] = None,
        end_date: Optional[Union[datetime, date]] = None,
) -> str:
    """
    更新租车预订

    修改租车的开始和结束日期
    """
    conn = connect(db)
    cursor = conn.cursor()

    if start_date:
        cursor.execute(
            "UPDATE car_rentals SET start_date = ? WHERE id = ?",
            (start_date, rental_id),
        )
    if end_date:
        cursor.execute(
            "UPDATE car_rentals SET end_date = ? WHERE id = ?", (end_date, rental_id)
        )

    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"租车 {rental_id} 成功更新。"
    else:
        conn.close()
        return f"未找到ID为 {rental_id} 的租车服务。"


@tool
def cancel_car_rental(rental_id: int) -> str:
    """
    取消租车预订

    将租车预订状态标记为未预订
    """
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute("UPDATE car_rentals SET booked = 0 WHERE id = ?", (rental_id,))
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"租车 {rental_id} 已取消。"
    else:
        conn.close()
        return f"未找到ID为 {rental_id} 的租车服务。"