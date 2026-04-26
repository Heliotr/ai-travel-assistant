"""
公司政策向量检索工具模块
使用向量相似度匹配，实现基于语义的公司政策查询
"""

import os
import re
from pathlib import Path

import numpy as np
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

# 从环境变量获取 API 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')

# 获取项目根目录
basic_dir = Path(__file__).resolve().parent.parent

# 读取FAQ文本文件
faq_text = None
with open(f'{basic_dir}/order_faq.md', encoding='utf8') as f:
    faq_text = f.read()

# 将FAQ文本按标题分割成多个文档
docs = [{"page_content": txt} for txt in re.split(r"(?=\n##)", faq_text)]


# 创建OpenAI Embedding模型
embeddings_model = OpenAIEmbeddings(
    openai_api_key=OPENAI_API_KEY,
    openai_api_base=OPENAI_BASE_URL,
)


class VectorStoreRetriever:
    """
    向量存储检索器类

    使用简单的余弦相似度计算进行文档检索
    """

    def __init__(self, docs: list, vectors: list):
        self._arr = np.array(vectors)  # 文档向量矩阵
        self._docs = docs              # 文档列表

    @classmethod
    def from_docs(cls, docs):
        """从文档列表创建检索器"""
        embeddings = embeddings_model.embed_documents([doc["page_content"] for doc in docs])
        vectors = embeddings
        return cls(docs, vectors)

    def query(self, query: str, k: int = 5) -> list[dict]:
        """
        查询相似文档

        参数:
            query: 查询文本
            k: 返回前k个最相似的文档

        返回:
            包含文档内容和相似度分数的列表
        """
        # 对查询生成嵌入向量
        embed = embeddings_model.embed_query(query)
        # 计算查询向量与文档向量的相似度
        scores = np.array(embed) @ self._arr.T
        # 获取相似度最高的k个文档索引
        top_k_idx = np.argpartition(scores, -k)[-k:]
        top_k_idx_sorted = top_k_idx[np.argsort(-scores[top_k_idx])]
        # 返回相似度最高的k个文档
        return [
            {**self._docs[idx], "similarity": scores[idx]} for idx in top_k_idx_sorted
        ]


# 创建向量检索器实例
retriever = VectorStoreRetriever.from_docs(docs)


@tool
def lookup_policy(query: str) -> str:
    """
    查询公司政策

    在进行航班变更或其他写操作之前使用此函数，
    检查某些选项是否允许

    参数:
        query: 查询内容

    返回:
        匹配的公司政策文档内容
    """
    # 查询相似度最高的2个文档
    docs = retriever.query(query, k=2)
    # 返回文档内容
    return "\n\n".join([doc["page_content"] for doc in docs])


if __name__ == '__main__':
    # 测试
    print(lookup_policy.invoke('怎么才能退票呢？'))