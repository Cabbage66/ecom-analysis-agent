from openai import OpenAI

from app.config import Settings


def complete_text(system_prompt: str, user_prompt: str) -> str:
    """接收系统生成SQL规则与用户问题，调用大模型并返回完整输出"""
    if not all(Settings.LLM_API_KEY, Settings.LLM_BASE_URL, Settings.LLM_MODEL):
        raise ValueError("模型相关配置错误")
    if Settings.LLM_TIMEOUT_SECONDS <= 0:
        raise ValueError("大模型超时时间配置需大于0")

    with OpenAI(
        base_url=Settings.LLM_BASE_URL,
        api_key=Settings.LLM_API_KEY,
        timeout=Settings.LLM_TIMEOUT_SECONDS,
        max_retries=0,  # 失败直接返回
    ) as client:
        response = client.chat.completions.create(
            model=Settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
        )
        if not response.choices:
            raise ValueError("模型没有返回结果")
        choice = response.choices[0]
        if choice.finish_reason != "stop":
            raise ValueError("模型返回不正确")
        content = choice.message.content
        if not isinstance(content, str) or not content.strip():
            raise ValueError("模型没有返回有效文本")
        return content.strip()
