from langchain_openai import ChatOpenAI

from new_graph_chat.env_utils import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

# 当前使用 DeepSeek Reasoner
llm = ChatOpenAI(
    # model='deepseek-reasoner',
    model='deepseek-chat',
    temperature=0.8,
    api_key=DEEPSEEK_API_KEY,
    base_url=DEEPSEEK_BASE_URL,
)