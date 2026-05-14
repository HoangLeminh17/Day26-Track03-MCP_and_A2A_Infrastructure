"""Shared LLM factory for all agents.

Prefers the OpenAI API when OPENAI_API_KEY is set.
Falls back to OpenRouter when OPENROUTER_API_KEY is set.
"""

import os

from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    """Return a ChatOpenAI client pointed at OpenAI or OpenRouter."""
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=openai_api_key,
            max_tokens=500,
            temperature=0.3,
        )

    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4-5"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        max_tokens=500,
        temperature=0.3,
    )
