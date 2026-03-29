"""
template-agent — LangGraph agent graph definition
Story: STORY-001
Agent: CodeGenAgent
"""
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic

from .state import TemplateAgentState
from .nodes import fetch_data, process, format_output


def build_graph() -> StateGraph:
    """Build and compile the template-agent graph."""
    model = ChatAnthropic(model="claude-3-5-sonnet-20241022")

    graph = StateGraph(TemplateAgentState)

    # Add nodes — one function per node
    graph.add_node("fetch",   fetch_data.run)
    graph.add_node("process", process.run)
    graph.add_node("output",  format_output.run)

    # Define edges
    graph.set_entry_point("fetch")
    graph.add_edge("fetch",   "process")
    graph.add_edge("process", "output")
    graph.add_edge("output",  END)

    # Compile with memory checkpointing
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# Module-level compiled graph — import and invoke directly
graph = build_graph()
