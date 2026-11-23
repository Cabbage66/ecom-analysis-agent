from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services import chat_service

router = APIRouter(prefix="/chat", tags=["AI对话"])


@router.post("/stream")
def chat_stream(
    body: ChatRequest, current_user: Annotated[User, Depends(get_current_user)]
):
    """流式问答，返回标准sse输出"""
    return StreamingResponse(
        chat_service.stream_chat(question=body.question, user_id=current_user.id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
