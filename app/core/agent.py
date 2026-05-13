# app/core/agent.py
import logging
from typing import Annotated
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from typing_extensions import TypedDict

from app.config import GROQ_API_KEY, LLM_MODEL
from app.core.tools import TOOLS
from app.core.prompts import APPOINTMENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def get_llm():
    llm = ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL, temperature=0.3)
    return llm.bind_tools(TOOLS)


def llm_node(state: AgentState) -> dict:
    messages = [SystemMessage(content=APPOINTMENT_SYSTEM_PROMPT)] + state["messages"]
    llm = get_llm()
    response = llm.invoke(messages)
    logger.info(
        f"Agent response — tool calls: "
        f"{len(response.tool_calls) if hasattr(response, 'tool_calls') else 0}"
    )
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        logger.info(f"Routing to tools: {[tc['name'] for tc in last.tool_calls]}")
        return "tools"
    return END


_agent = None


def get_agent():
    global _agent
    if _agent is None:
        memory = MemorySaver()
        tool_node = ToolNode(TOOLS)

        graph = StateGraph(AgentState)
        graph.add_node("llm", llm_node)
        graph.add_node("tools", tool_node)
        graph.set_entry_point("llm")
        graph.add_conditional_edges("llm", should_continue, {"tools": "tools", END: END})
        graph.add_edge("tools", "llm")

        _agent = graph.compile(checkpointer=memory)
        logger.info("Appointment agent compiled")
    return _agent


def chat(message: str, session_id: str) -> dict:
    """
    Send a message to the appointment agent.
    Returns the response text and any booking details.
    """
    agent = get_agent()
    config = {
        "configurable": {"thread_id": session_id},
        "recursion_limit": 15,
    }

    result = agent.invoke(
        {"messages": [HumanMessage(content=message)]},
        config=config,
    )

    final_message = result["messages"][-1]
    response_text = final_message.content

    # Extract booking confirmation if present
    booking_confirmed = None
    if "[BOOKING_CONFIRMED:" in response_text:
        response_text = response_text.split("[BOOKING_CONFIRMED:")[0].strip()
        booking_confirmed = True

    # Clean slots data marker from response
    if "[SLOTS_DATA:" in response_text:
        response_text = response_text.split("[SLOTS_DATA:")[0].strip()

    tools_used = []
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                tools_used.append(tc["name"])

    return {
        "response": response_text,
        "session_id": session_id,
        "tools_used": tools_used,
        "booking_confirmed": booking_confirmed,
    }