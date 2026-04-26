"""
网络搜索工具模块
使用智谱AI的Web Search API实现网络搜索功能
"""

import os
from typing import Type

import zhipuai
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI

# 从环境变量获取 API Key
ZHIPU_API_KEY = os.getenv('ZHIPU_API_KEY')

# 创建智谱AI客户端
if ZHIPU_API_KEY:
    zhihuiai_client = ZhipuAI(api_key=ZHIPU_API_KEY)
else:
    zhihuiai_client = None


class SearchArgs(BaseModel):
    """搜索工具的参数模型"""
    query: str = Field(description="需要进行网络搜索的信息")


class MySearchTool(BaseTool):
    """
    网络搜索工具
    使用智谱AI的Web Search API进行联网搜索
    """

    name: str = "search_tool"
    description: str = "搜索互联网上公开内容的工具"
    args_schema: Type[BaseModel] = SearchArgs

    def _run(self, query: str) -> str:
        """
        执行网络搜索

        参数:
            query: 搜索关键词

        返回:
            搜索结果文本，多条结果用换行分隔
        """
        if not zhihuiai_client:
            return "网络搜索工具未配置 API Key"

        try:
            print("执行搜索工具，搜索词：", query)
            response = zhihuiai_client.web_search.web_search(
                search_engine="search_pro",  # 使用专业搜索
                search_query=query,
            )
            print(response)
            if response.search_result:
                return "\n\n".join([d.content for d in response.search_result])
            return "没有搜索到任何内容"
        except Exception as e:
            print(e)
            return f"搜索出错: {str(e)}"


# 导出工具实例
_search_tool_instance = None


def get_search_tool():
    """获取搜索工具单例"""
    global _search_tool_instance
    if _search_tool_instance is None:
        _search_tool_instance = MySearchTool()
    return _search_tool_instance