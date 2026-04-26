from typing import Annotated
from datetime import datetime

from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import SystemMessage
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.types import Command

from new_graph_chat.my_llm import llm
from new_graph_chat.checkpoint_config import checkpointer  # 导入统一的 checkpointer
from tools.car_tools import search_car_rentals, book_car_rental, update_car_rental, cancel_car_rental
from tools.flights_tools import search_flights, update_ticket_to_new_flight, cancel_ticket
from tools.hotels_tools import search_hotels, book_hotel, update_hotel, cancel_hotel
from tools.retriever_vector import lookup_policy
from tools.net_search_tool import MySearchTool
from tools.trip_tools import search_trip_recommendations, book_excursion, update_excursion, cancel_excursion


def get_user_info_prompt(user_info: str | None) -> str:
    """生成用户信息提示"""
    if user_info:
        return f"\n\n当前用户的航班信息:\n<Flights>\n{user_info}\n</Flights>"
    return ""


def create_dynamic_prompt(base_prompt: str, user_info: str | None = None) -> str:
    """创建动态提示词，包含用户信息和当前时间"""
    user_info_section = get_user_info_prompt(user_info)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{base_prompt}{user_info_section}\n当前时间: {current_time}"

# 网络搜索的 子智能体
RESEARCH_AGENT_PROMPT = (
    "你是一个专业的网络搜索智能体(Agent)。\n\n"
    "## 职责\n"
    "负责处理所有需要网络数据获取的任务，包括：\n"
    "- 网络搜索和查询\n"
    "- 获取最新信息\n"
    "- 数据收集和整理\n\n"
    "## 处理规则\n"
    "1. 使用搜索工具获取最新、最准确的信息\n"
    "2. 对搜索结果进行整理和总结\n"
    "3. 回复时仅包含工作结果，不要包含任何其他文字\n"
    "4. 如果搜索无结果，明确告知用户\n"
)

research_agent = create_react_agent(
    model=llm,
    tools=[MySearchTool()],
    prompt=RESEARCH_AGENT_PROMPT,
    checkpointer=checkpointer,
    name="research_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
update_flight_safe_tools = [search_flights, lookup_policy]
update_flight_sensitive_tools = [update_ticket_to_new_flight, cancel_ticket]

# 合并所有工具
update_flight_tools = update_flight_safe_tools + update_flight_sensitive_tools

# 航班预订的 子智能体
FLIGHT_AGENT_PROMPT = (
    "你是专业的航班顾问，负责处理航班查询、预订、改签、取消等业务。\n\n"

    "## 可用工具\n"
    "- search_flights: 搜索航班（只读操作）\n"
    "- lookup_policy: 查询公司政策（只读操作）\n"
    "- update_ticket_to_new_flight: 改签机票（敏感操作，需要用户确认）\n"
    "- cancel_ticket: 取消机票（敏感操作，需要用户确认）\n\n"

    "## 上下文工程规则\n\n"

    "1. **基于已有信息处理**（最重要）：\n"
    "   - 用户已提供的信息（如出发地、目的地、日期）直接使用\n"
    "   - 不要重复询问用户已提供的信息\n"
    "   - 如果信息不足，先用已有信息尝试查询，结果为空时再追问\n"
    "   - 用户说\"那改成后天\"，理解是指修改日期\n"
    "   - 用户说\"第一个\"、\"第二个\"，理解是指选择列表中的选项\n\n"

    "2. **多轮对话记忆**：\n"
    "   - 你可以访问对话历史，记住用户之前提到的所有信息\n"
    "   - 如果用户在当前对话中已经提供了目的地，不要再问\n"
    "   - 用户说\"继续\"或\"是的\"，通常是确认之前的操作\n\n"

    "3. **查询优先原则**：\n"
    "   - 优先调用搜索工具获取结果\n"
    "   - 如果第一次查询无结果，扩大搜索范围再试\n"
    "   - 查到结果后直接展示，不要额外追问细节\n\n"

    "4. **敏感操作确认**：\n"
    "   - 改签和取消是敏感操作，执行前必须告知用户具体信息\n"
    "   - 展示要操作的航班号、时间等关键信息\n"
    "   - 等待用户确认后再执行\n\n"

    "5. **禁止事项**：\n"
    "   - 不要每次都重新查询用户自己的航班信息\n"
    "   - 不要在已有足够信息时还追问细节\n"
    "   - 不要询问用户已经明确说出的信息\n\n"

    f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    "请根据用户需求处理航班业务，记住充分利用上下文信息。"
)

flight_booking_agent = create_react_agent(
    model=llm,
    tools=update_flight_tools,
    prompt=FLIGHT_AGENT_PROMPT,
    checkpointer=checkpointer,
    name="flight_booking_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
book_hotel_safe_tools = [search_hotels]
book_hotel_sensitive_tools = [book_hotel, update_hotel, cancel_hotel]

# 合并所有工具
book_hotel_tools = book_hotel_safe_tools + book_hotel_sensitive_tools

# 酒店处理的 子智能体
HOTEL_AGENT_PROMPT = (
    "你是专业的酒店顾问，负责处理酒店查询、预订、修改、取消等业务。\n\n"

    "## 可用工具\n"
    "- search_hotels: 搜索酒店（只读操作）\n"
    "- book_hotel: 预订酒店（敏感操作，需要用户确认）\n"
    "- update_hotel: 修改酒店预订（敏感操作，需要用户确认）\n"
    "- cancel_hotel: 取消酒店预订（敏感操作，需要用户确认）\n\n"

    "## 上下文工程规则\n\n"

    "1. **基于已有信息处理**（最重要）：\n"
    "   - 用户已提供的信息直接使用，不要重复询问\n"
    "   - 如果信息不足，先尝试查询，结果为空时再追问\n"
    "   - 用户说\"换一家\"、\"第二个\"，理解是指选择\n\n"

    "2. **多轮对话记忆**：\n"
    "   - 你可以访问对话历史，记住用户之前提到的所有信息\n"
    "   - 如果用户在当前对话中已经提供了城市，不要再问\n\n"

    "3. **查询优先原则**：\n"
    "   - 优先调用搜索工具获取结果\n"
    "   - 查到结果后直接展示价格和房型，不要额外追问\n\n"

    "4. **敏感操作确认**：\n"
    "   - 预订、修改、取消是敏感操作，执行前先展示关键信息\n"
    "   - 等待用户确认后再执行\n\n"

    "5. **禁止事项**：\n"
    "   - 不要重复询问用户已经明确说出的信息\n"
    "   - 不要在已有足够信息时还追问细节\n\n"

    f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    "请根据用户需求处理酒店业务，记住充分利用上下文信息。"
)

hotel_booking_agent = create_react_agent(
    model=llm,
    tools=book_hotel_tools,
    prompt=HOTEL_AGENT_PROMPT,
    checkpointer=checkpointer,
    name="hotel_booking_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
book_car_rental_safe_tools = [search_car_rentals]
book_car_rental_sensitive_tools = [
    book_car_rental,
    update_car_rental,
    cancel_car_rental,
]

# 合并所有工具
book_car_rental_tools = book_car_rental_safe_tools + book_car_rental_sensitive_tools
# 汽车租赁处理的 子智能体
CAR_RENTAL_AGENT_PROMPT = (
    "你是专业的租车顾问，负责处理租车查询、预订、修改、取消等业务。\n\n"

    "## 可用工具\n"
    "- search_car_rentals: 搜索租车（只读操作）\n"
    "- book_car_rental: 预订租车（敏感操作，需要用户确认）\n"
    "- update_car_rental: 修改租车订单（敏感操作，需要用户确认）\n"
    "- cancel_car_rental: 取消租车订单（敏感操作，需要用户确认）\n\n"

    "## 处理规则\n\n"

    "1. **基于已有信息处理**：\n"
    "   - 用户已提供的信息（如城市、日期、车型）直接使用\n"
    "   - 不要重复询问用户已提供的信息\n"
    "   - 如果信息不足，先尝试查询，再根据结果追问\n\n"

    "2. **多轮对话**：\n"
    "   - 记住对话历史中用户提到的所有信息\n"
    "   - 用户说\"换成SUV\"、\"要紧凑型\"，理解是指车型偏好\n\n"

    "3. **查询优先**：\n"
    "   - 优先调用搜索工具获取可用车辆\n"
    "   - 查到结果后直接展示车型和价格\n\n"

    "4. **敏感操作处理**：\n"
    "   - 预订、修改、取消是敏感操作\n"
    "   - 执行前先展示租车信息、价格等关键信息\n"
    "   - 等待用户确认后再执行\n\n"

    "请根据用户需求处理租车业务。"
)

car_rental_booking_agent = create_react_agent(
    model=llm,
    tools=book_car_rental_tools,
    prompt=CAR_RENTAL_AGENT_PROMPT,
    checkpointer=checkpointer,
    name="car_rental_booking_agent",
)

# 定义安全工具（只读操作）和敏感工具（涉及更改的操作）
book_excursion_safe_tools = [search_trip_recommendations]
book_excursion_sensitive_tools = [book_excursion, update_excursion, cancel_excursion]

# 合并所有工具
book_excursion_tools = book_excursion_safe_tools + book_excursion_sensitive_tools
# 旅行推荐处理的 子智能体
EXCURSION_AGENT_PROMPT = (
    "你是专业的旅行顾问，负责处理旅行推荐、景点预订等业务。\n\n"

    "## 可用工具\n"
    "- search_trip_recommendations: 搜索旅行推荐（只读操作）\n"
    "- book_excursion: 预订行程（敏感操作，需要用户确认）\n"
    "- update_excursion: 修改行程预订（敏感操作，需要用户确认）\n"
    "- cancel_excursion: 取消行程预订（敏感操作，需要用户确认）\n\n"

    "## 处理规则\n\n"

    "1. **基于已有信息处理**：\n"
    "   - 用户已提供的信息（如目的地、日期、人数）直接使用\n"
    "   - 不要重复询问用户已提供的信息\n\n"

    "2. **多轮对话**：\n"
    "   - 记住对话历史中用户提到的所有信息\n"
    "   - 用户说\"那个行程\"、\"第一个\"，理解是指选择\n\n"

    "3. **查询优先**：\n"
    "   - 优先调用搜索工具获取推荐\n"
    "   - 查到结果后直接展示行程和价格\n\n"

    "4. **敏感操作处理**：\n"
    "   - 预订、修改、取消是敏感操作\n"
    "   - 执行前先展示行程详情、价格等关键信息\n"
    "   - 等待用户确认后再执行\n\n"

    "请根据用户需求处理旅行推荐业务。"
)

excursion_booking_agent = create_react_agent(
    model=llm,
    tools=book_excursion_tools,
    prompt=EXCURSION_AGENT_PROMPT,
    checkpointer=checkpointer,
    name="excursion_booking_agent",
)

def create_handoff_tool(*, agent_name: str, description: str | None = None):
    """
    创建一个用于将当前会话转接到指定代理的工具函数。

    该函数返回一个装饰器包装的工具函数，当调用时会生成一个工具消息并返回转接命令，
    指示流程控制器将控制权转移给指定的代理。

    参数:
        agent_name (str): 目标代理的名称，用于标识要转接的代理
        description (str | None): 工具的描述信息，如果未提供则使用默认描述

    返回:
        handoff_tool: 一个装饰器包装的工具函数，用于执行转接操作
    """
    name = f"transfer_to_{agent_name}"
    description = description or f"Ask {agent_name} for help."

    @tool(name, description=description)
    def handoff_tool(
            state: Annotated[MessagesState, InjectedState],
            tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        """
        执行实际的转接操作。

        创建一个工具消息表明转接成功，并返回一个命令对象指示流程控制器
        将控制权转移给指定代理，同时更新会话状态。

        参数:
            state (MessagesState): 当前会话状态，包含消息历史等信息
            tool_call_id (str): 工具调用的唯一标识符

        返回:
            Command: 包含转接指令和状态更新的命令对象
        """
        # 构造工具消息，记录转接操作的成功执行
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        # 返回转接命令，指定目标代理和更新后的状态
        return Command(
            goto=agent_name,
            update={**state, "messages": state["messages"] + [tool_message]},
            graph=Command.PARENT,
        )

    return handoff_tool


# Handoffs
assign_to_research_agent = create_handoff_tool(
    agent_name="research_agent",
    description="将任务分配给：research_agent智能体。",
)

assign_to_flight_booking_agent = create_handoff_tool(
    agent_name="flight_booking_agent",
    description="将任务分配给：flight_booking_agent智能体。",
)
assign_to_hotel_booking_agent = create_handoff_tool(
    agent_name="hotel_booking_agent",
    description="将任务分配给：hotel_booking_agent智能体。",
)
assign_to_car_rental_booking_agent = create_handoff_tool(
    agent_name="car_rental_booking_agent",
    description="将任务分配给：car_rental_booking_agent智能体。",
)
assign_to_excursion_booking_agent = create_handoff_tool(
    agent_name="excursion_booking_agent",
    description="将任务分配给：excursion_booking_agent智能体。",
)

# 主管智能体提示词
SUPERVISOR_PROMPT = (
    "你是一个旅行助手主管(Supervisor)，你的职责是根据用户需求，将任务**转交给**合适的子助理来处理，并在子助理完成后**总结结果输出给用户**。\n\n"

    "## 子助理分类\n"
    "- **research_agent**: 网络搜索、信息查询、获取最新资讯\n"
    "- **flight_booking_agent**: 航班查询、预订、改签、取消\n"
    "- **hotel_booking_agent**: 酒店查询、预订、修改、取消\n"
    "- **car_rental_booking_agent**: 租车服务查询、预订、修改、取消\n"
    "- **excursion_booking_agent**: 旅行推荐、景点预订\n\n"

    "## 你的工作流程\n\n"

    "**场景1：用户首次请求**\n"
    "1. 根据用户意图判断需要哪个子助理处理\n"
    "2. 调用对应的转交工具，将任务交给子助理\n"
    "3. 你的回复应该只是简短说明要将任务转交给谁\n\n"

    "**场景2：子助理已完成处理**\n"
    "1. 子助理处理完成后，会返回结果给你\n"
    "2. 你需要读取对话历史中子助理的回复内容\n"
    "3. 将结果进行**总结和格式化输出**给用户\n"
    "4. 输出时使用清晰的结构（如表格、列表等）\n"
    "5. 如果用户需要进一步操作（如预订），引导用户确认\n\n"

    "## 路由规则\n\n"

    "1. **根据用户意图快速判断**：\n"
    "   - 用户提到\"航班\"、\"机票\"、\"飞行\"、\"飞机\" → 转交给 flight_booking_agent\n"
    "   - 用户提到\"酒店\"、\"住宿\"、\"房间\"、\"宾馆\" → 转交给 hotel_booking_agent\n"
    "   - 用户提到\"租车\"、\"汽车\"、\"用车\"、\"自驾\" → 转交给 car_rental_booking_agent\n"
    "   - 用户提到\"旅行\"、\"景点\"、\"旅游\"、\"游玩\"、\"行程\" → 转交给 excursion_booking_agent\n"
    "   - 用户只是问一般信息或需要最新信息（如天气、新闻）→ 转交给 research_agent\n\n"

    "2. **多轮对话处理**：\n"
    "   - 如果用户已经与某个子助理对话中，继续转交给同一个子助理\n"
    "   - 记住对话上下文，避免重复询问已提供的信息\n"
    "   - 如果用户说\"继续\"、\"是的\"、\"确认\"，说明是在回应之前的对话\n\n"

    "3. **简单回复直接回复**：\n"
    "   - 如果用户只是打招呼（你好、hi等），直接友好回复\n"
    "   - 如果问题无需调用工具，直接回答即可\n"
    "   - 问候语示例：\"您好！我是旅行助手，有什么可以帮您的吗？\"\n\n"

    "现在请根据用户的需求，决定将任务转交给哪个子助理，或者总结子助理的处理结果输出给用户。\n"
    "记住：\n"
    "- 首次请求时转交给子助理\n"
    "- 子助理完成后总结结果输出给用户\n"
    "- 输出要结构化、清晰"
)

# 主管 智能体 - 负责路由，将任务分配给合适的子助理
supervisor_agent = create_react_agent(
    model=llm,
    tools=[
        assign_to_research_agent,
        assign_to_flight_booking_agent,
        assign_to_hotel_booking_agent,
        assign_to_car_rental_booking_agent,
        assign_to_excursion_booking_agent
    ],
    prompt=SUPERVISOR_PROMPT,
    checkpointer=checkpointer,
    name="supervisor",
)