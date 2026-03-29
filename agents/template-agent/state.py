"""
State schema for template-agent.
All state is immutable — nodes return updated copies, never mutate in place.
"""
from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages


class TemplateAgentState(TypedDict):
    """
    State flows through every node in the graph.
    Add fields here as the agent needs more context.
    """
    # Input
    input: str

    # Conversation history (append-only via add_messages reducer)
    messages: Annotated[list, add_messages]

    # Working data — populated by nodes
    data: Optional[dict]
    result: Optional[str]

    # Metadata
    error: Optional[str]
    iteration: int
