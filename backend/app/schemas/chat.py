from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """流式对话请求模型"""

    question: str = Field(min_length=1, max_length=1000, description="用户问题")
