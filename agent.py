"""
agent.py — LangGraph ReAct agent for Sahaba Islamic Assistant.

Creates a compiled LangGraph graph that:
  - Uses gpt-5-nano-2025-08-07 with all 17 API tools
  - Adapts its system prompt to the selected configuration (A / B / C)
  - Logs all LLM inputs and outputs to the terminal
  - Supports multi-turn conversation memory via message history
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.graph import StateGraph, MessagesState, END
from langgraph.prebuilt import ToolNode, tools_condition

from config import OPENAI_API_KEY, CHAT_MODEL, CONFIG_A, CONFIG_B, CONFIG_C
from api_tools import ALL_TOOLS

# ─── System Prompts per Configuration ─────────────────────────────────────────

_SYSTEM_PROMPT_BASE = """You are Sahaba, a knowledgeable and compassionate Islamic assistant.
You help users with Quranic verses, prayer times, the Islamic calendar, Qibla direction, 
and general questions about Islam.

Guidelines:
- Always be respectful, accurate, and grounded in authoritative Islamic sources.
- When quoting Quran, always provide both the Arabic text and English translation.
- Format prayer timetables as markdown tables.
- When the user mentions a location, use the geocode_address tool first to get coordinates,
  then use those coordinates for prayer times, Qibla, etc.
- Today's date is {today}. Use this when the user asks about 'today' or 'now'.
- If the user asks about Quran recitation audio, use get_ayah_recitation_url and return the URL.
- For Qibla compass image, use get_qibla_compass_image_url — the app will render it.
- Always greet warmly and respond with Bismillah spirit."""

_SYSTEM_PROMPT_C = """You are Sahaba, a warm conversational Islamic companion.
You adapt your tone to be friendly, empathetic, and encouraging — like speaking with a knowledgeable 
Muslim friend. You help with Quranic verses, prayer times, the Islamic calendar, Qibla direction,
and meaningful Islamic conversation.

Guidelines:
- Always be respectful, accurate, and grounded in authoritative Islamic sources.
- When quoting Quran, always provide both the Arabic text and English translation.
- Format prayer timetables as markdown tables.
- When the user mentions a location, use geocode_address first to get coordinates.
- Today's date is {today}. Use this when the user asks about 'today' or 'now'.
- If the user asks about Quran recitation audio, use get_ayah_recitation_url and return the URL.
- For Qibla compass image, use get_qibla_compass_image_url — the app will render it visually.
- Be warm, conversational, and encouraging. Use gentle Islamic greetings naturally.
- If the user seems to need dua or spiritual support, offer it generously."""


def _get_system_prompt(config_mode: str, today: str) -> str:
    if config_mode == CONFIG_C:
        return _SYSTEM_PROMPT_C.format(today=today)
    return _SYSTEM_PROMPT_BASE.format(today=today)


# ─── LLM + Tool Binding ───────────────────────────────────────────────────────

def _build_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=CHAT_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=0.7,
    ).bind_tools(ALL_TOOLS)


# ─── Graph Nodes ──────────────────────────────────────────────────────────────

def _make_call_model(llm, system_prompt: str):
    """Return a node function that calls the LLM and logs I/O."""
    def call_model(state: MessagesState):
        messages = state["messages"]
        full_messages = [SystemMessage(content=system_prompt)] + messages

        print(f"\n[LLM] Calling {CHAT_MODEL}")
        print(f"  Messages in context: {len(full_messages)}")
        last_human = next(
            (m.content for m in reversed(messages) if isinstance(m, HumanMessage)), ""
        )
        print(f"  Last user message: {str(last_human)[:200]}")

        response = llm.invoke(full_messages)

        print(f"  → Response type: {type(response).__name__}")
        if hasattr(response, "content") and response.content:
            print(f"  → Content: {str(response.content)[:300]}")
        if hasattr(response, "tool_calls") and response.tool_calls:
            for tc in response.tool_calls:
                print(f"  → Tool call: {tc['name']}({tc.get('args', {})})")

        return {"messages": [response]}

    return call_model


# ─── Graph Builder ────────────────────────────────────────────────────────────

def create_agent(config_mode: str, today: str):
    """Build and compile a LangGraph ReAct agent for the given configuration.

    Args:
        config_mode: One of 'A', 'B', or 'C'
        today: Today's date string (DD-MM-YYYY) for the system prompt

    Returns:
        Compiled LangGraph CompiledGraph ready for .invoke()
    """
    system_prompt = _get_system_prompt(config_mode, today)
    llm = _build_llm()

    tool_node = ToolNode(ALL_TOOLS)

    builder = StateGraph(MessagesState)
    builder.add_node("agent", _make_call_model(llm, system_prompt))
    builder.add_node("tools", tool_node)

    builder.set_entry_point("agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    graph = builder.compile()
    return graph


def run_agent(graph, messages: list, user_input: str) -> tuple[str, list]:
    """Run one turn of the agent.

    Args:
        graph: Compiled LangGraph graph
        messages: Existing conversation history (list of LangChain message objects)
        user_input: The latest user message text

    Returns:
        (ai_text_response, updated_messages_list)
    """
    print(f"\n[AGENT] User input: {user_input[:300]}")

    new_messages = messages + [HumanMessage(content=user_input)]
    result = graph.invoke({"messages": new_messages})
    updated = result["messages"]

    # Extract the final AI text response
    ai_response = ""
    for msg in reversed(updated):
        if isinstance(msg, AIMessage) and msg.content:
            ai_response = msg.content
            break

    print(f"[AGENT] Final response: {ai_response[:300]}{'...' if len(ai_response) > 300 else ''}")
    return ai_response, updated
