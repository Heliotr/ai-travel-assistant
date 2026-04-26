"""
新工作流 API 视图
使用 LangGraph 新版多智能体架构
支持 SSE 流式响应
"""

import logging
import json
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from new_graph_chat.graph import (
    execute_graph_stream,
    create_session_config,
    execute_graph,
)
from api.graph_api.graph_schemas import BaseGraphSchema
from langgraph.types import Command

# 创建路由
router = APIRouter()
log = logging.getLogger('new_graph')


def format_sse_event(event_type: str, **kwargs) -> str:
    """格式化 SSE 事件数据"""
    data = {'type': event_type, **kwargs}
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post('/new_graph/stream/', description='流式调用新工作流', summary='新工作流流式调用')
async def execute_new_graph_stream(request: Request, obj_in: BaseGraphSchema):
    """
    流式执行新工作流接口
    通过 SSE 实时推送 AI 响应、工具调用等信息到前端
    """
    question = obj_in.user_input
    config = obj_in.config.model_dump() if obj_in.config else {}

    # 如果没有提供 thread_id，创建新的
    if 'configurable' not in config:
        config['configurable'] = {}
    if 'thread_id' not in config['configurable']:
        config['configurable']['thread_id'] = f"thread_{id(obj_in)}"
    if 'passenger_id' not in config['configurable']:
        config['configurable']['passenger_id'] = "3442 587242"

    log.info(f"[New Graph Stream Start] Question: {question[:50] if question else 'confirm'}...")
    log.info(f"[New Graph Stream] Config: {config}")

    # 检查是否是确认回答
    is_confirm = question.strip().lower() == 'y'

    def generate_stream():
        try:
            # 流式执行 - 使用列表收集所有事件确保完整性
            all_events = []
            for event in execute_graph_stream(question, config):
                all_events.append(event)

            log.info(f"Collected {len(all_events)} events, now yielding")
            for e in all_events:
                log.info(f"  Event: {e.get('type')}")

            # 然后逐个发送
            for event in all_events:
                event_type = event.get('type', '')
                log.info(f"[Stream] Yielding: {event_type}")

                if event_type == 'agent':
                    yield format_sse_event('agent', agent=event.get('agent', ''))
                elif event_type == 'tool':
                    yield format_sse_event('tool', agent=event.get('agent', 'unknown'), tool=event.get('tool', ''))
                elif event_type == 'tool_result':
                    yield format_sse_event('tool_result', tool=event.get('tool', ''), content=event.get('content', ''))
                elif event_type == 'content':
                    yield format_sse_event('content', content=event.get('content', ''), agent=event.get('agent', 'unknown'))
                elif event_type == 'confirm':
                    yield format_sse_event('confirm', content=event.get('content', ''))
                elif event_type == 'end':
                    yield format_sse_event('end')
                elif event_type == 'error':
                    yield format_sse_event('error', message=event.get('message', '未知错误'))

            log.info(f"[Stream] Completed, total events: {len(all_events)}")

        except Exception as e:
            log.error(f"[New Graph Error] {e}", exc_info=True)
            yield format_sse_event('error', message=str(e))
            return

        log.info("[New Graph Stream End]")

    return StreamingResponse(
        generate_stream(),
        media_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'
        }
    )


@router.post('/new_graph/', description='同步调用新工作流', summary='新工作流同步调用')
async def execute_new_graph(request: Request, obj_in: BaseGraphSchema):
    """
    同步执行新工作流接口（非流式）
    返回完整响应
    """
    question = obj_in.user_input
    config = obj_in.config.model_dump() if obj_in.config else {}

    # 如果没有提供 thread_id，创建新的
    if 'configurable' not in config:
        config['configurable'] = {}
    if 'thread_id' not in config['configurable']:
        config['configurable']['thread_id'] = f"thread_{id(obj_in)}"
    if 'passenger_id' not in config['configurable']:
        config['configurable']['passenger_id'] = "3442 587242"

    log.info(f"[New Graph Sync] Question: {question}")

    try:
        result = execute_graph(question, config)
        return {
            'assistant': result.get('response', ''),
            'interrupted': result.get('interrupted', False),
            'error': result.get('error'),
        }
    except Exception as e:
        log.error(f"[New Graph Sync Error] {e}", exc_info=True)
        return {'assistant': f"发生错误: {str(e)}", 'error': str(e)}