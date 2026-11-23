import json
from typing import Any, Generator

FIXED_REPLY = "已经接收到问题：{question}，当前为对话骨架，未接入大模型"


def _sse(event: str, data: dict[str, Any]) -> str:
    """按sse的标准格式拼接事件输出，event行+data行+空行"""
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata:{payload}\n\n"


def _reply_chunks(text: str, size: int = 8) -> Generator[str, None, None]:
    """顺序返回回复片段"""
    for i in range(0, len(text), size):
        yield text[i : i + size]


def stream_chat(
    question: str, user_id: int | None = None
) -> Generator[str, None, None]:
    """SSE对话，按协议下发对话事件"""
    if not question.strip():
        yield _sse(event="error", data={"message": "对话内容不能为空"})
        return

    yield _sse(event="status", data={"message": "已收到，正在分析"})

    reply = FIXED_REPLY.format(question=question.strip())

    for piece in _reply_chunks(reply):
        yield _sse(event="token", data={"content": piece})

    yield _sse(event="done", data={})
