"""
Tool: ExampleTool
LangChain tool — can be bound to any LLM that supports tool calling.
"""
from langchain_core.tools import tool
import structlog

log = structlog.get_logger()


@tool
def example_tool(input: str) -> str:
    """
    ExampleTool tool.

    Args:
        input: Description of what the tool receives

    Returns:
        Description of what the tool returns
    """
    log.info("tool.example_tool", input=input)

    # TODO: implement tool logic
    return f"ExampleTool result for: {input}"
