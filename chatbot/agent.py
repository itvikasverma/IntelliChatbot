from functools import lru_cache

from langchain_core.messages import HumanMessage, ToolMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from chatbot.config import get_settings
from chatbot.tools import build_tools


@lru_cache(maxsize=1)
def build_agent():
    settings = get_settings()
    model = ChatGroq(
        model=settings.groq_model,
        api_key=settings.groq_api_key,
        temperature=0.2,
    )

    return create_react_agent(
        model=model,
        tools=build_tools(),
        checkpointer=MemorySaver(),
        prompt=settings.chatbot_system_prompt,
    )


def chat(message: str, thread_id: str = "default") -> tuple[str, list[str]]:
    result = build_agent().invoke(
        {"messages": [HumanMessage(content=message)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    
    # Extract tool names from the message history
    tools_used = []
    print(f"\n=== DEBUG: Message History ===")
    for i, msg in enumerate(result["messages"]):
        print(f"[{i}] {type(msg).__name__}: {msg.__class__.__name__}")
        
        # Check for AIMessage with tool_calls
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"    Found tool_calls: {msg.tool_calls}")
            for tool_call in msg.tool_calls:
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name") or tool_call.get("tool")
                else:
                    tool_name = getattr(tool_call, "name", None) or getattr(tool_call, "tool", None)
                print(f"    Tool: {tool_name}")
                if tool_name and tool_name not in tools_used:
                    tools_used.append(tool_name)
        # Also check for ToolMessage which contains the tool name
        elif isinstance(msg, ToolMessage):
            print(f"    ToolMessage - Name: {msg.name}")
            tool_name = msg.name
            if tool_name and tool_name not in tools_used:
                tools_used.append(tool_name)
    
    print(f"=== Tools Used: {tools_used} ===\n")
    return result["messages"][-1].content, tools_used


def stream_chat(message: str, thread_id: str = "default"):
    """Stream tool calls and final response as they happen."""
    result = build_agent().invoke(
        {"messages": [HumanMessage(content=message)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    
    tools_used = []
    
    # Stream events as tools are called
    for msg in result["messages"]:
        print(f"[STREAM] Processing {type(msg).__name__}")
        
        # Capture tool calls
        if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            print(f"[STREAM] Found tool_calls: {msg.tool_calls}")
            for tool_call in msg.tool_calls:
                if isinstance(tool_call, dict):
                    tool_name = tool_call.get("name") or tool_call.get("tool")
                else:
                    tool_name = getattr(tool_call, "name", None) or getattr(tool_call, "tool", None)
                
                if tool_name and tool_name not in tools_used:
                    tools_used.append(tool_name)
                    print(f"[STREAM] Yielding tool_start: {tool_name}")
                    yield {
                        "type": "tool_start",
                        "tool": tool_name,
                        "tools_used": tools_used,
                    }
        
        # Capture tool completions
        elif isinstance(msg, ToolMessage):
            tool_name = msg.name
            if tool_name:
                print(f"[STREAM] Yielding tool_end: {tool_name}")
                yield {
                    "type": "tool_end",
                    "tool": tool_name,
                    "tools_used": tools_used,
                }
    
    # Final response
    print(f"[STREAM] Yielding response")
    yield {
        "type": "response",
        "answer": result["messages"][-1].content,
        "tools_used": tools_used,
    }
