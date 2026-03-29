"""
Node: format_output
Receives state, performs one focused action, returns updated state.
Never mutates state in place — always return a dict of updated fields.
"""
import structlog
from ..state import TemplateAgentState

log = structlog.get_logger()


async def run(state: TemplateAgentState) -> dict:
    """
    format_output node.
    Input:  state['input'] or state['data']
    Output: updated state fields
    """
    log.info("format_output.start", input=state.get("input"))

    try:
        # TODO: implement node logic here
        result = state.get("input", "")

        log.info("format_output.complete", result=result)
        return {"result": result, "error": None}

    except Exception as e:
        log.error("format_output.error", error=str(e))
        return {"error": str(e)}
