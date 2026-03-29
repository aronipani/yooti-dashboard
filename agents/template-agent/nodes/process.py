"""
Node: process
Receives state, performs one focused action, returns updated state.
Never mutates state in place — always return a dict of updated fields.
"""
import structlog
from ..state import TemplateAgentState

log = structlog.get_logger()


async def run(state: TemplateAgentState) -> dict:
    """
    process node.
    Input:  state['input'] or state['data']
    Output: updated state fields
    """
    log.info("process.start", input=state.get("input"))

    try:
        # TODO: implement node logic here
        result = state.get("input", "")

        log.info("process.complete", result=result)
        return {"result": result, "error": None}

    except Exception as e:
        log.error("process.error", error=str(e))
        return {"error": str(e)}
