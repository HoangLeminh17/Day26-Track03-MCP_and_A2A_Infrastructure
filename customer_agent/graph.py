"""Customer Agent graph definition."""

from __future__ import annotations

import logging
from typing import Any

from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

from common.llm import get_llm

logger = logging.getLogger(__name__)

CUSTOMER_SYSTEM_PROMPT = """You are a helpful legal assistant at the front desk of a multi-agent
legal services platform. Your job is to:

1. Understand the user's legal question
2. Determine if it needs specialist legal analysis (contract issues, tax law,
   regulatory compliance, corporate liability, etc.)
3. If so, use the `delegate_to_legal_agent` tool to send it to the Law Agent,
   which will coordinate specialist sub-agents (Tax and Compliance) as needed
4. Present the comprehensive response clearly to the user

Always use the `delegate_to_legal_agent` tool for any substantive legal question.
Do not attempt to answer complex legal questions from your own knowledge alone.

Be professional, clear, and make the specialist response accessible to the user.
"""


def build_graph(trace_id: str, context_id: str, depth: int) -> Any:
    """Build an agent graph with request trace context bound into the tool closure."""

    @tool
    async def delegate_to_legal_agent(question: str) -> str:
        """Send a legal question to the Law Agent for comprehensive analysis."""
        from common.a2a_client import delegate
        from common.registry_client import discover

        logger.info(
            "Customer delegate_to_legal_agent | trace=%s context=%s depth=%d",
            trace_id,
            context_id,
            depth,
        )

        try:
            endpoint = await discover("legal_question")
            result = await delegate(
                endpoint=endpoint,
                question=question,
                context_id=context_id,
                trace_id=trace_id,
                depth=depth + 1,
            )
            if not result:
                return "The Law Agent returned an empty response. Please try again."
            return result
        except Exception as exc:
            logger.exception("delegate_to_legal_agent failed: %s", exc)
            return f"Could not reach the Law Agent: {exc}"

    llm = get_llm()
    return create_react_agent(
        model=llm,
        tools=[delegate_to_legal_agent],
        prompt=CUSTOMER_SYSTEM_PROMPT,
    )
