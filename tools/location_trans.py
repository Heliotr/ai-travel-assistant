"""
城市名称转换工具模块
支持中文和英文城市名称的相互转换
"""

from typing import Optional, List

# 中文到英文的城市映射
CITY_MAP = {
    '北京': 'Beijing',
    '上海': 'Shanghai',
    '广州': 'Guangzhou',
    '深圳': 'Shenzhen',
    '成都': 'Chengdu',
    '重庆': 'Chongqing',
    '杭州': 'Hangzhou',
    '南京': 'Nanjing',
    '武汉': 'Wuhan',
    '西安': 'XiAn',
    '天津': 'Tianjin',
    '大连': 'Dalian',
    '青岛': 'Qingdao',
    '济南': 'Jinan',
    '郑州': 'Zhengzhou',
    '长沙': 'Changsha',
    '沈阳': 'Shenyang',
    '哈尔滨': 'Harbin',
    '昆明': 'Kunming',
    '贵阳': 'Guiyang',
    '厦门': 'Xiamen',
    '珠海': 'Zhuhai',
    '三亚': 'Sanya',
    '海口': 'Haikou',
    '苏州': 'Suzhou',
    '无锡': 'Wuxi',
    '宁波': 'Ningbo',
    '温州': 'Wenzhou',
    '东莞': 'Dongguan',
    '佛山': 'Foshan',
}

# 反向映射：英文 -> 中文
ENGLISH_TO_CHINESE = {v: k for k, v in CITY_MAP.items()}


def transform_location(location: Optional[str]) -> str:
    """
    转换城市名称

    参数:
        location: 输入的城市名称（中文或英文）

    返回:
        转换后的城市名称，如果是纯中文则转英文，否则保持原样
    """
    if not location:
        return ""

    # 如果是纯中文，转换为英文
    if all('\u4e00' <= char <= '\u9fff' for char in location):
        return CITY_MAP.get(location, location)

    # 如果是英文，直接返回
    return location


def get_all_variants(location: Optional[str]) -> List[str]:
    """
    获取城市名的所有变体（中英文）

    用于在数据库搜索时同时匹配中文和英文

    参数:
        location: 输入的城市名称

    返回:
        包含中英文变体的列表
    """
    if not location:
        return []

    variants = []

    # 检查是否是中文
    is_chinese = all('\u4e00' <= char <= '\u9fff' for char in location) if location else False

    if is_chinese:
        # 中文 -> 添加中文和英文
        variants.append(location)
        english = CITY_MAP.get(location)
        if english:
            variants.append(english)
    else:
        # 英文 -> 添加英文和中文
        variants.append(location)
        chinese = ENGLISH_TO_CHINESE.get(location)
        if chinese:
            variants.append(chinese)

    return variants if variants else [location]