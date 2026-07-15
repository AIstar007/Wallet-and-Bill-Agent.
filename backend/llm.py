"""
Azure OpenAI LLM wrapper.

Supports:
- Standard completion (llm_call)
- Streaming completion (llm_stream)

Returns None if Azure OpenAI is not configured so the application can
fall back to its stub responses.
"""

import os
from typing import Generator

_client = None


def _get_client():
    global _client

    if _client is None:
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")

        if not all([api_key, endpoint, api_version]):
            return None

        from openai import AzureOpenAI

        _client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=endpoint,
            api_version=api_version,
        )

    return _client


def llm_call(system_prompt: str, user_message: str) -> str | None:
    """
    Standard (non-streaming) response.
    """
    client = _get_client()

    if client is None:
        return None

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def llm_stream(
    system_prompt: str,
    user_message: str,
) -> Generator[str, None, None]:
    """
    Streaming Azure OpenAI response.

    Yields text chunks as they arrive.
    """

    client = _get_client()

    if client is None:
        return

    stream = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ],
        temperature=0.3,
        stream=True,
    )

    for chunk in stream:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta.content

        if delta:
            yield delta
