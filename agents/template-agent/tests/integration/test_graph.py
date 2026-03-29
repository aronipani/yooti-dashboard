"""
Integration tests for template-agent graph.
Tests the full graph end-to-end with mocked LLM responses.
Uses recorded LLM responses (VCR-style) to avoid real API calls in CI.
"""
import pytest
from unittest.mock import patch, AsyncMock
from agents.template_agent.graph import build_graph
from agents.template_agent.state import TemplateAgentState


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for integration tests — no real API calls."""
    with patch('langchain_anthropic.ChatAnthropic.ainvoke') as mock:
        mock.return_value = AsyncMock(content="mocked LLM response")
        yield mock


@pytest.fixture
def graph_instance():
    return build_graph()


@pytest.fixture
def thread_config():
    return {"configurable": {"thread_id": "integration-test-1"}}


class TestFullGraph:

    @pytest.mark.asyncio
    async def test_graph_runs_to_completion(
        self, graph_instance, thread_config, mock_llm_response
    ):
        """Full graph executes without error."""
        state = TemplateAgentState(
            input="integration test input",
            messages=[], data=None, result=None, error=None, iteration=0
        )
        result = await graph_instance.ainvoke(state, thread_config)
        assert result is not None
        assert result.get("error") is None

    @pytest.mark.asyncio
    async def test_graph_state_flows_correctly(
        self, graph_instance, thread_config, mock_llm_response
    ):
        """State is passed and updated correctly between nodes."""
        state = TemplateAgentState(
            input="state flow test",
            messages=[], data=None, result=None, error=None, iteration=0
        )
        result = await graph_instance.ainvoke(state, thread_config)
        # Input should still be in final state
        assert result.get("input") == "state flow test"
