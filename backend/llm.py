"""
Real LLM call wrapper using Azure OpenAI. Returns None if the required
Azure OpenAI environment variables are not set, so /chat falls back
to its stub logic and the whole stack still runs with zero setup.
"""

import os

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
    client = _get_client()

    if client is None:
        return None

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content
