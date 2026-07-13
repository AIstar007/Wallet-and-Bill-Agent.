"""
Real LLM call wrapper — same pattern as the AI Engineer submission. Returns
None if no API key is set, so /chat falls back to its stub logic and the
whole stack still runs with zero setup.
"""
import os

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return None
        from openai import OpenAI
        _client = OpenAI(api_key=api_key)
    return _client


def llm_call(system_prompt: str, user_message: str, model: str = "gpt-4o-mini") -> str:
    client = _get_client()
    if client is None:
        return None
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content
