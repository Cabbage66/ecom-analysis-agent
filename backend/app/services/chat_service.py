import json
from typing import Any, Generator

from openai import APIError

from app.services import nl2sql_service

# FIXED_REPLY = "已经接收到问题：{question}，当前为对话骨架，未接入大模型"


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

    yield _sse(event="status", data={"message": "已收到，正在分析，准备生成查询"})

    try:
        sql = nl2sql_service.generate_sql(question=question)
    except ValueError as exc:
        yield _sse("error", {"message": str(exc)})
        return
    except APIError:
        yield _sse(
            "error", {"message": "大模型调用失败，请检查服务地址、模型的状态和API余额"}
        )
        return
    except Exception:
        yield _sse("error", {"message": "生成SQL失败，请稍后重试"})
        return

    yield _sse("status", "SQL生成成功，等待执行")
    reply = f"生成SQL \n{sql}"
    # reply = FIXED_REPLY.format(question=question.strip())

    for piece in _reply_chunks(reply):
        yield _sse(event="token", data={"content": piece})

    yield _sse(event="done", data={})
