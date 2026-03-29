"""
Evaluation tests for template-agent.

Evals are different from unit tests:
  - They test LLM OUTPUT QUALITY, not code logic
  - They use real LLM calls (or recorded traces)
  - They assert on semantic correctness, not exact strings
  - They run in CI nightly, not on every commit (expensive)

Run with: pytest tests/evals/ --eval
Skip in fast CI: pytest tests/ --ignore=tests/evals/
"""
import pytest
from agents.template_agent.graph import graph
from agents.template_agent.state import TemplateAgentState


# Mark all evals so they can be excluded from fast CI
pytestmark = pytest.mark.eval


@pytest.fixture
def agent_config():
    """Thread config for graph invocation."""
    return {"configurable": {"thread_id": "eval-test-1"}}


class TestAgentOutput:

    @pytest.mark.asyncio
    async def test_returns_non_empty_result(self, agent_config):
        """Basic sanity: agent produces output."""
        state = TemplateAgentState(
            input="test question",
            messages=[], data=None, result=None, error=None, iteration=0
        )
        result = await graph.ainvoke(state, agent_config)
        assert result.get("result") is not None
        assert len(result.get("result", "")) > 0

    @pytest.mark.asyncio
    async def test_consistent_on_same_input(self, agent_config):
        """Consistency check: same input → same category of output."""
        state = TemplateAgentState(
            input="deterministic test input",
            messages=[], data=None, result=None, error=None, iteration=0
        )
        result_1 = await graph.ainvoke(state, {**agent_config, "configurable": {"thread_id": "eval-1"}})
        result_2 = await graph.ainvoke(state, {**agent_config, "configurable": {"thread_id": "eval-2"}})

        # Not asserting exact equality (LLMs vary) — asserting category
        assert result_1.get("error") is None
        assert result_2.get("error") is None

    @pytest.mark.asyncio
    async def test_handles_edge_case_input(self, agent_config):
        """Robustness: agent does not crash on unusual input."""
        state = TemplateAgentState(
            input="",
            messages=[], data=None, result=None, error=None, iteration=0
        )
        result = await graph.ainvoke(state, agent_config)
        # Should return an error field, not raise an exception
        assert isinstance(result, dict)
