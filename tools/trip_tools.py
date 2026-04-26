"""
旅行推荐相关工具模块
提供旅行推荐搜索、预订、更新和取消等功能
"""

from sqlite3 import connect
from typing import Optional, List

from langchain_core.tools import tool

from tools import db
from tools.location_trans import get_all_variants


@tool
def search_trip_recommendations(
        location: Optional[str] = None,
        name: Optional[str] = None,
        keywords: Optional[str] = None,
        limit: int = 10,
) -> List[dict]:
    """
    搜索旅行推荐

    根据位置、名称和关键词搜索旅行推荐，支持中英文匹配。
    默认返回10条结果，避免返回过多数据。

    参数:
        location: 景点位置（城市名）
        name: 景点名称关键词
        keywords: 关键词搜索（逗号分隔）
        limit: 返回结果数量限制，默认10条
    """
    conn = connect(db)
    cursor = conn.cursor()

    # 获取中英文变体
    location_variants = get_all_variants(location)
    query = "SELECT * FROM trip_recommendations WHERE 1=1"
    params = []

    if location_variants:
        conditions = " OR ".join(["location LIKE ?" for _ in location_variants])
        query += f" AND ({conditions})"
        params.extend([f"%{v}%" for v in location_variants])
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if keywords:
        keyword_list = keywords.split(",")
        keyword_conditions = " OR ".join(["keywords LIKE ?" for _ in keyword_list])
        query += f" AND ({keyword_conditions})"
        params.extend([f"%{keyword.strip()}%" for keyword in keyword_list])

    query += " ORDER BY id LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    results = cursor.fetchall()

    conn.close()

    # 压缩结果，只返回关键信息
    compressed_results = []
    for row in results:
        full_dict = dict(zip([column[0] for column in cursor.description], row))
        compressed_results.append({
            'id': full_dict.get('id'),
            'name': full_dict.get('name', '')[:40],
            'location': full_dict.get('location'),
            'category': full_dict.get('category'),
            'keywords': full_dict.get('keywords', '')[:50] if full_dict.get('keywords') else None,
            'booked': full_dict.get('booked'),
        })

    return compressed_results


@tool
def book_excursion(recommendation_id: int) -> str:
    """
    预订旅行推荐

    根据推荐ID标记为已预订
    """
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE trip_recommendations SET booked = 1 WHERE id = ?", (recommendation_id,)
    )
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"旅行推荐 {recommendation_id} 成功预订。"
    else:
        conn.close()
        return f"未找到ID为 {recommendation_id} 的旅行推荐。"


@tool
def update_excursion(recommendation_id: int, details: str) -> str:
    """
    更新旅行推荐详情
    """
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE trip_recommendations SET details = ? WHERE id = ?",
        (details, recommendation_id),
    )
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"旅行推荐 {recommendation_id} 成功更新。"
    else:
        conn.close()
        return f"未找到ID为 {recommendation_id} 的旅行推荐。"


@tool
def cancel_excursion(recommendation_id: int) -> str:
    """
    取消旅行推荐预订
    """
    conn = connect(db)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE trip_recommendations SET booked = 0 WHERE id = ?", (recommendation_id,)
    )
    conn.commit()

    if cursor.rowcount > 0:
        conn.close()
        return f"旅行推荐 {recommendation_id} 已取消。"
    else:
        conn.close()
        return f"未找到ID为 {recommendation_id} 的旅行推荐。"