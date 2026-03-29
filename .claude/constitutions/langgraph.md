# LangGraph Agent Constitution — yooti-dashboard

## Purpose
Defines how LangGraph agents are built in this project.
Agent reads this when building or modifying any agent graph.
These rules exist because agent failures in production are hard to debug
and can be expensive. The patterns here make agents testable, resumable,
and auditable.

---

## The fundamental rules

STATE IS IMMUTABLE
  Nodes receive state and return a dict of updated fields.
  Never mutate state in place. Always return new values.
  Wrong: state["count"] += 1                                 ✗
  Right: return {"count": state["count"] + 1}                ✓

ONE NODE, ONE RESPONSIBILITY
  A node that does two things should be two nodes.
  Maximum 50 lines per node function (excluding docstring).
  If a node needs helper functions, extract them to a utils file.

ERRORS ARE STATE, NOT EXCEPTIONS
  Every node catches all exceptions.
  Errors are returned as state fields, not raised.
  Wrong: raise ValueError("something failed")                ✗
  Right: return {"error": "something failed", "status": "failed"}  ✓
  The graph routes on the error field.

PROMPTS ARE FILES, NOT STRINGS
  System prompts live in prompts/ as versioned .txt files.
  Load them at graph construction time, not hardcoded inline.
  Wrong: system_prompt = "You are a helpful assistant..."    ✗ (inline)
  Right: system_prompt = Path("prompts/analyst.txt").read_text()  ✓

---

## Node structure — every node follows this template

  import structlog
  from ..state import AgentState

  log = structlog.get_logger()

  async def run(state: AgentState) -> dict:
      """
      One-line description of what this node does.
      Input:  state fields this node reads
      Output: state fields this node updates
      """
      log.info("node_name.start", relevant_field=state.get("field"))

      try:
          # implementation
          result = await do_the_work(state)
          log.info("node_name.complete", result_summary=str(result)[:100])
          return {"result": result, "error": None}

      except Exception as e:
          log.error("node_name.failed", error=str(e))
          return {"error": str(e), "status": "failed"}

---

## State schema rules

Define state as TypedDict with explicit types for every field.
Every field must have a clear purpose — document it.
Input fields at the top. Working fields in the middle. Output at the bottom.
Use Annotated[list, add_messages] for message history — never a plain list.
Include an error field (Optional[str]) in every state schema.
Include an iteration counter (int, default 0) for self-healing loops.

---

## Graph construction rules

Build the graph in graph.py — do not import the compiled graph from nodes.
Compile once at module level: graph = build_graph()
Use MemorySaver for all graphs — resumability is required.
Set entry point explicitly with set_entry_point().
Every graph must have an END edge — never leave a node dangling.
Conditional edges must handle all possible return values explicitly.

---

## Tool rules

Every tool is a standalone function decorated with @tool.
Tools live in tools/ directory — one tool per file for complex tools.
Every tool has a complete docstring — the LLM reads it to decide when to call.
Every tool catches its own exceptions and returns an error string.
Tools are unit tested independently — no graph needed to test a tool.

  @tool
  def get_property_data(property_id: str) -> str:
      """
      Retrieves property data including price, location, and attributes.
      Returns JSON string with property details, or error message if not found.
      Args:
          property_id: The unique property identifier (format: PROP-NNN)
      """
      try:
          ...
      except Exception as e:
          return f"Error retrieving property {property_id}: {str(e)}"

---

## Testing — three layers, all required

UNIT TESTS (tests/unit/)
  Test every node function in isolation.
  Mock all LLM calls — no real API calls.
  Mock all external services.
  Run on every commit — must be fast (< 2 seconds per test).

INTEGRATION TESTS (tests/integration/)
  Test the full graph end-to-end.
  Mock LLM responses with patch().
  Verify state flows correctly between nodes.
  Verify final state has expected fields.
  Run on every PR.

EVALS (tests/evals/)
  Test LLM output quality with real API calls.
  Mark with: pytestmark = pytest.mark.eval
  Assert semantic correctness — not exact strings.
  Run nightly via CI schedule — never on every commit.
  Require ANTHROPIC_API_KEY or OPENAI_API_KEY in environment.

---

## Observability — required

Set these in .env for automatic LangSmith tracing:
  LANGCHAIN_TRACING_V2=true
  LANGCHAIN_API_KEY=...
  LANGCHAIN_PROJECT=yooti-dashboard

Do not add manual trace calls — LangSmith instruments automatically.
Log entry and exit of every node with structlog.
The combination of LangSmith traces and structlog gives complete visibility.

---

## Multi-agent coordination — requires architect approval

A graph calling another graph is an architectural decision.
Do not implement multi-agent patterns autonomously.
Write an escalation file and wait for architect review.
The architect must approve the state contract between agents.

---

## What is banned

Hardcoded system prompts in Python files
Node functions that mutate state directly
Raising exceptions instead of returning error state
LLM calls outside of node functions or tools
Blocking synchronous operations inside async nodes
Graph construction inside node functions
Direct database access in node functions — use tools
Any node function over 50 lines (excluding docstring and logging)
